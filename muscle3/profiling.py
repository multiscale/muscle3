import sqlite3
from pathlib import Path
from typing import cast, List, Optional, Tuple

import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

from libmuscle import ProfileDatabase


def plot_instances(performance_file: Path) -> None:
    """Plot instances

    Reads data from the database and makes a bar chart with for each
    instance how much time it spend running, waiting, and
    communicating.

    This won't actually show the plot until show_plots() is called.

    Args:
        performance_file: Database to load data from.
    """
    with ProfileDatabase(performance_file) as db:
        instances, compute, transfer, wait = db.instance_stats()

    fig, ax = plt.subplots()

    width = 0.5
    bottom = np.zeros(len(instances))
    ax.bar(instances, compute, width, label='Compute', bottom=bottom)
    bottom += compute
    ax.bar(instances, transfer, width, label='Transfer', bottom=bottom)
    bottom += transfer
    ax.bar(instances, wait, width, label='Wait', bottom=bottom)
    ax.set_title('Simulation component time breakdown')
    ax.set_xlabel('Instance')
    ax.tick_params(axis='x', labelrotation = 45)
    for label in ax.xaxis.get_ticklabels():
        label.set_horizontalalignment('right')
    ax.set_ylabel('Total time (s)')
    fig.legend(loc='outside right center')
    # bottom=0.3 leaves space for x-axis labels
    # right=0.8 leaves 20% for the legend
    fig.subplots_adjust(bottom=0.3, right=0.8)


def plot_resources(performance_file: Path) -> None:
    """Plot resources

    Reads data from the database and makes a bar chart with for each
    resource (CPU core) which instances ran on it for how long.

    This won't actually show the plot until show_plots() is called.

    Args:
        performance_file: Database to load data from.
    """
    with ProfileDatabase(performance_file) as db:
        stats = db.resource_stats()

    palette = dict()
    next_color = 0
    for core, data in stats.items():
        for instance in data.keys():
            if instance not in palette:
                palette[instance] = f'C{next_color}'
                next_color += 1

    fig, ax = plt.subplots()

    seen_instances = set()
    for i, core in enumerate(sorted(stats.keys())):
        bottom = 0.0
        for instance, time in sorted(stats[core].items(), key=lambda x: -x[1]):
            if instance not in seen_instances:
                label: Optional[str] = instance
                seen_instances.add(instance)
            else:
                label = '_'

            ax.bar(
                    i, time, _BAR_WIDTH,
                    label=label, bottom=bottom, color=palette[instance])
            bottom += time

    ax.set_xticks(range(len(stats)))
    ax.set_xticklabels(stats.keys())

    ax.set_title('Per-core time breakdown')
    ax.set_xlabel('Core')
    ax.tick_params(axis='x', labelrotation = 45)
    for tick_label in ax.xaxis.get_ticklabels():
        tick_label.set_horizontalalignment('right')
    ax.set_ylabel('Total time (s)')
    fig.legend(loc='outside right center')
    # bottom=0.3 leaves space for x-axis labels
    # right=0.8 leaves 20% for the legend
    fig.subplots_adjust(bottom=0.3, right=0.8)


_EVENT_TYPES = (
        'REGISTER', 'CONNECT', 'SHUTDOWN_WAIT', 'DISCONNECT_WAIT', 'SHUTDOWN',
        'DEREGISTER', 'SEND', 'RECEIVE_WAIT', 'RECEIVE_TRANSFER', 'RECEIVE_DECODE')


_EVENT_PALETTE = {
        'REGISTER': '#910f33',
        'CONNECT': '#c85172',
        'SHUTDOWN_WAIT': '#ffdddd',
        'DISCONNECT_WAIT': '#eedddd',
        'SHUTDOWN': '#c85172',
        'DEREGISTER': '#910f33',
        'RECEIVE_WAIT': '#cccccc',
        'RECEIVE_TRANSFER': '#ff7d00',
        'RECEIVE_DECODE': '#ccff00',
        'SEND': '#0095bf'}


_MAX_EVENTS = 5000


_CUTOFF_TEXT = (
        'Warning: data was omitted from the plot in the\n crosshatched'
        ' areas to improve performance.\n Please zoom or pan using the'
        ' tools at the bottom\n of the window to see the missing events.'
        )


_BAR_WIDTH = 0.8


class TimelinePlot:
    """Manages an interactive timeline

    This implements on-demand loading of events as the user pans and
    zooms.
    """
    def __init__(self, performance_file: Path) -> None:
        """Create a TimelinePlot

        This plots the dark gray background bars, and then plots the
        rest on top on demand.

        Args:
            performance_file: The database to plot
        """
        fig, ax = plt.subplots()
        # right=0.8 leaves 20% for the legend
        fig.subplots_adjust(right=0.67)
        self._ax = ax

        # Y axis
        self._cur = sqlite3.connect(performance_file).cursor()
        self._cur.execute("SELECT oid, name FROM instances ORDER BY oid")
        instance_ids, instance_names = zip(*self._cur.fetchall())

        ax.set_yticks(instance_ids)
        ax.set_yticklabels(instance_names)

        # Instances
        self._cur.execute("SELECT MIN(start_time) FROM events")
        self._min_db_time = self._cur.fetchall()[0][0]

        self._cur.execute(
                "SELECT instance_oid, (start_time - ?) * 1e-9"
                " FROM events AS e"
                " JOIN event_types AS et ON (e.event_type_oid = et.oid)"
                " WHERE et.name = 'REGISTER'", (self._min_db_time,))
        begin_times = dict(self._cur.fetchall())

        self._cur.execute(
                "SELECT instance_oid, (stop_time - ?) * 1e-9"
                " FROM events AS e"
                " JOIN event_types AS et ON (e.event_type_oid = et.oid)"
                " WHERE et.name = 'DEREGISTER'", (self._min_db_time,))
        end_times = dict(self._cur.fetchall())

        instances = sorted(begin_times.keys())
        self._instances = instances

        if not begin_times:
            raise RuntimeError(
                    'This database appears to be empty. Did the simulation crash'
                    ' before any data were generated?')

        # Rest of plot
        ax.set_title('Execution timeline')
        ax.set_xlabel('Wallclock time (s)')

        # Background
        running_artist = ax.barh(
                instances,
                [end_times[i] - begin_times[i] for i in instances],
                _BAR_WIDTH,
                left=[begin_times[i] for i in instances],
                label='RUNNING', color='#444444'
                )

        # Initial events plot
        xmin = min(begin_times.values())
        self._global_xmax = max(end_times.values())

        first_cutoff = float('inf')
        self._bars = dict()
        for event_type in _EVENT_TYPES:
            instances, start_times, durations, cutoff = self.get_data(
                    event_type, xmin, self._global_xmax)

            if not instances:
                # Work around https://github.com/matplotlib/matplotlib/issues/21506
                instances = ['']
                start_times = [float('NaN')]
                durations = [float('NaN')]

            self._bars[event_type] = ax.barh(
                    instances, durations, _BAR_WIDTH,
                    label=event_type, left=start_times,
                    color=_EVENT_PALETTE[event_type])
            if cutoff:
                first_cutoff = min(first_cutoff, cutoff)

        # Initial cut-off area
        if first_cutoff != float('inf'):
            self._bars['_CUTOFF'] = ax.barh(
                    self._instances, self._global_xmax - first_cutoff, _BAR_WIDTH,
                    label='Not shown', left=first_cutoff,
                    color='#FFFFFF', hatch='x')
            self._cutoff_warning = ax.text(
                    0.02, 0.02, _CUTOFF_TEXT, transform=ax.transAxes, fontsize=12,
                    verticalalignment='bottom', horizontalalignment='left', wrap=True,
                    bbox={
                        'facecolor': '#ffcccc', 'alpha': 0.75})

        ax.set_autoscale_on(True)
        ax.callbacks.connect('xlim_changed', self.update_data)

        ordered_artists = [self._bars[event_type][0] for event_type in _EVENT_TYPES]
        ordered_names = list(_EVENT_TYPES)

        ordered_artists.insert(6, running_artist)
        ordered_names.insert(6, 'RUNNING')

        fig.legend(
                ordered_artists, ordered_names, loc='outside right center',
                bbox_to_anchor=(1.0, 0.6))
        cast(Figure, ax.figure).canvas.draw_idle()

    def close(self) -> None:
        """Closes the database connection"""
        self._cur.close()

    def get_data(
            self, event_type: str, xmin: float, xmax: float
            ) -> Tuple[List[int], List[float], List[float], Optional[float]]:
        """Get events from the database

        Returns three lists with instance oid, start time and duration, and
        the last timepoint returned in case we had too much data to show and
        data got cut off, or None if all matching data was returned.

        Args:
            event_type: Type of events to get
            xmin: Time point after which the event must have stopped
            xmax: Time point before which the event must have started
        """
        self._cur.execute(
                "SELECT"
                "  instance_oid, (start_time - ?) * 1e-9,"
                "  (stop_time - start_time) * 1e-9"
                " FROM events AS e"
                " JOIN event_types AS et ON (e.event_type_oid = et.oid)"
                " WHERE et.name = ?"
                " AND (start_time - ?) * 1e-9 <= ?"
                " AND ? <= (stop_time - ?) * 1e-9"
                " ORDER BY start_time ASC"
                " LIMIT ?",
                (
                    self._min_db_time, event_type, self._min_db_time, xmax,
                    xmin, self._min_db_time, _MAX_EVENTS))
        results = self._cur.fetchall()
        if not results:
            return list(), list(), list(), None

        if len(results) == _MAX_EVENTS:
            return tuple(zip(*results)) + (results[-1][1],)    # type: ignore

        return tuple(zip(*results)) + (None,)    # type: ignore

    def update_data(self, ax: Axes) -> None:
        """Update the plot after the axes have changed

        This is called after the user has panned or zoomed, and refreshes the
        plot.

        Args:
            ax: The Axes object we are drawing in
        """
        xmin, xmax = ax.viewLim.intervalx

        for event_type in _EVENT_TYPES:
            instances, start_times, durations, cutoff = self.get_data(
                    event_type, xmin, xmax)
            if instances:
                # update existing rectangles
                bars = self._bars[event_type].patches
                n_cur = len(instances)
                n_avail = len(bars)

                for i in range(min(n_cur, n_avail)):
                    bars[i].set_y(instances[i] - _BAR_WIDTH * 0.5)
                    bars[i].set_x(start_times[i])
                    bars[i].set_width(durations[i])
                    bars[i].set_visible(True)

                # set any superfluous ones invisible
                for i in range(n_cur, n_avail):
                    bars[i].set_visible(False)

            # update cutoff bars, if any
            if '_CUTOFF' in self._bars:
                bars = self._bars['_CUTOFF'].patches
                if cutoff:
                    for bar in bars:
                        bar.set_x(cutoff)
                        bar.set_width(self._global_xmax - cutoff)
                        bar.set_visible(True)
                    self._cutoff_warning.set_visible(True)
                else:
                    for bar in bars:
                        bar.set_visible(False)
                    self._cutoff_warning.set_visible(False)


tplot = None    # type: Optional[TimelinePlot]


def plot_timeline(performance_file: Path) -> None:
    global tplot
    tplot = TimelinePlot(performance_file)


def show_plots() -> None:
    """Actually show the plots on screen"""
    plt.show()      # type: ignore
    if tplot:
        tplot.close()
