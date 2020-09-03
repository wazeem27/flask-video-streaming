from collections import deque


class TemperatureQueue:
    """
    Temperature queue, for storing normalized temperature
    Queue size will be 10 by default.

    queue only append the temperature value if it within the human range
    Queueing and dequeueing in worst case scenario will be O(1) time
    """

    def __init__(self, max_size = 10):
        """
        Initialize this queue to the empty queue.
        Parameters
        ----------
        max_size : int
            Maximum number of items contained in this queue. Defaults to 10.
        """
        self._queue = deque(maxlen=max_size)
        self.min_temp = 97
        self.max_temp = 100

    def enqueue(self, item):
        """
        Queues the passed item (i.e., pushes this item onto the tail of this
        queue).

        If this queue is already full, the item at the head of this queue
        is silently removed from this queue *before* the passed item is
        queued.
        """
        self._queue.append(item)

    def __len__(self):
        """Return the length of the temperature queue"""
        return len(self._queue)

    def __str__(self):
        """String reqpresentation of the queue"""
        return "Queue -- {}, length-> {}".format(list(self._queue), len(self._queue))

    def average(self):
        """
        Average of the temperature queue
        """
        return round(sum(list(self._queue))/len(self._queue), 2) if len(self._queue) else 98.4

    def is_valid(self, value):
        """Check whether the incoming temperature is within the speified range"""
        return self.min_temp <= value and value <= self.max_temp
