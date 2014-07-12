from unittest import TestCase
import datetime

import nose
import numpy as np
try:
    import fastcluster
except ImportError:
    fastcluster = None

import blitzortung.db
import blitzortung.db.query
import blitzortung.clustering


class TestClustering(TestCase):
    def setUp(self):
        pass

    def test_clustering(self):
        if not fastcluster:
            raise nose.SkipTest("implement as an integration test later")

        strokes_db = blitzortung.db.stroke()
        now = datetime.datetime.utcnow()
        start_time = now - datetime.timedelta(hours=2)
        time_interval = blitzortung.db.query.TimeInterval(start_time)
        strokes = strokes_db.select(time_interval)

        self.clustering = blitzortung.clustering.Clustering(strokes)
        print(str(self.clustering))

    def test_basic_clustering(self):
        if not fastcluster:
            raise nose.SkipTest("implement as an integration test later")
        data = [
            [1.0, 2.0],
            [2.0, 1.0],
            [2.1, 1.1],
            [2, 1.1],
            [1.0, 2.1],
        ]
        data = np.array(data)

        dist = fastcluster.pdist(data)
        result = fastcluster.linkage(dist).tolist()

        print(result)

