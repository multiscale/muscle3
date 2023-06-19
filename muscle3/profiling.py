import sqlite3
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

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
    ax.set_ylabel('Total time (s)')
    ax.legend(loc='upper right')


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
        bottom = 0
        for instance, time in sorted(stats[core].items(), key=lambda x: -x[1]):
            if instance not in seen_instances:
                label: Optional[str] = instance
                seen_instances.add(instance)
            else:
                label = '_'

            ax.bar(
                    i, time, 0.8,
                    label=label, bottom=bottom, color=palette[instance])
            bottom += time

    ax.set_xticks(range(len(stats)))
    ax.set_xticklabels(stats.keys())

    ax.set_title('Per-core time breakdown')
    ax.set_xlabel('Core')
    ax.set_ylabel('Total time (s)')
    ax.legend(loc='upper right')


_EVENT_TYPES = (
        'REGISTER', 'CONNECT', 'DEREGISTER',
        'SEND', 'RECEIVE_WAIT', 'RECEIVE_TRANSFER', 'RECEIVE_DECODE')


_EVENT_PALETTE = {
        'REGISTER': '#910f33',
        'CONNECT': '#c85172',
        'DEREGISTER': '#910f33',
        'RECEIVE_WAIT': '#cccccc',
        'RECEIVE_TRANSFER': '#ff7d00',
        'RECEIVE_DECODE': '#ccff00',
        'SEND': '#0095bf'}


_MAX_EVENTS = 2000


def plot_timeline(performance_file: Path) -> None:
    with sqlite3.connect(performance_file) as conn:
        cur = conn.cursor()

        cur.execute("SELECT oid, name FROM instances ORDER BY oid")
        instance_ids, instance_names = zip(*cur.fetchall())

        cur.execute("SELECT MIN(start_time) FROM events")
        min_time = cur.fetchall()[0][0]

        cur.execute(
                "SELECT instance, (start_time - ?)"
                " FROM events AS e"
                " JOIN event_types AS et ON (e.event_type_oid = et.oid)"
                " WHERE et.name = 'REGISTER'", (min_time,))
        begin_times = dict(cur.fetchall())

        cur.execute(
                "SELECT instance, (stop_time - ?)"
                " FROM events AS e"
                " JOIN event_types AS et ON (e.event_type_oid = et.oid)"
                " WHERE et.name = 'DEREGISTER'", (min_time,))
        end_times = dict(cur.fetchall())

        fig, ax = plt.subplots()

        instances = sorted(begin_times.keys())
        ax.barh(
                instances,
                [(end_times[i] - begin_times[i]) * 1e-9 for i in instances],
                0.8,
                left=[begin_times[i] * 1e-9 for i in instances],
                label='RUNNING', color='#444444'
                )

        for event_type in _EVENT_TYPES:
            cur.execute(
                    "SELECT"
                    "  instance, (start_time - ?) * 1e-9,"
                    "  (stop_time - start_time) * 1e-9"
                    " FROM events AS e"
                    " JOIN event_types AS et ON (e.event_type_oid = et.oid)"
                    " WHERE et.name = ?"
                    " ORDER BY start_time ASC"
                    " LIMIT ?",
                    (min_time, event_type, _MAX_EVENTS))
            instances, start_times, durations = zip(*cur.fetchall())

            if len(instances) == _MAX_EVENTS:
                print(
                        'Warning: event data truncated. Sorry, we cannot yet show'
                        ' this amount of data efficiently enough.')
            ax.barh(
                    instances, durations, 0.8,
                    label=event_type, left=start_times,
                    color=_EVENT_PALETTE[event_type])

        ax.set_yticks(instance_ids)
        ax.set_yticklabels(instance_names)

        ax.set_title('Execution timeline')
        ax.set_xlabel('Wallclock time (s)')

        ax.legend(loc='upper right')


def show_plots() -> None:
    """Actually show the plots on screen"""
    plt.show()
