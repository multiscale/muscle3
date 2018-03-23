from pathlib import Path
import sys

# Add libmuscle to the Python path, it seems pytest doesn't add it
# automatically if you're in a parallel directory like here.
sys.path.append(str(Path(__file__).parent / '..' / 'libmuscle' / 'python'))
