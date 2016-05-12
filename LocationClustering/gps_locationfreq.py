#!/usr/bin/env python3
"""
    command: 
    output map file to: 
"""
import datetime
import numpy
import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
sys.path.append(PACKAGE_PARENT)

import Liu.custommodule.cluster as ccluster
import Liu.custommodule.cpygmaps as cpygmaps
import Liu.custommodule.fuzzycmeans as cfuzzy
import Liu.custommodule.location as clocation
import Liu.custommodule.user as cuser

"""parameters"""
FILTER_TIME = 1443657600 # 2015/10/01 1448928000 # 2015/12/01
CLUSTER_NUM = 30
ERROR = 0.0001
MAX_KTH = 30

"""file path"""
USER_POSTS_FILE = "./data/TravelerPosts"
OUTPUT_MAP = "./data/LocationCluster/LocationMapCoor_" + str(CLUSTER_NUM) +\
    "k" + str(MAX_KTH) + "e" + str(ERROR) + ".html"
OUTPUT_CLUSTER = "./data/LocationCluster/LocationClusterCoor_" + str(CLUSTER_NUM) +\
    "k" + str(MAX_KTH) + "e" + str(ERROR) + ".txt"

def set_location_user_count(locations):
    for key in locations.keys():
        users = set(a_post.uid for a_post in locations[key].posts)
        setattr(locations[key], "usercount", len(users))

def main():
    print("--------------------------------------")
    print("STARTTIME:", (datetime.datetime.now()))
    print("--------------------------------------")
    
    # getting data
    locations = clocation.open_locations()
    users = cuser.open_users_posts_afile(USER_POSTS_FILE)

    print("Sampling users posts...")
    for key, a_user in users.items():
        posts = [x for x in a_user.posts if (x.time > FILTER_TIME) and (x.time < 1451606400)]
        users[key].posts = posts
    locations = clocation.fit_users_to_location(locations, users, "uid")
    set_location_user_count(locations)

    coordinate = numpy.array([(float(x.lat), float(x.lng)) for x in locations.values()])
    location_frequency = numpy.array([x.usercount for x in locations.values()])
    
    # intersect clustering with the kth locations in each cluster & location frequency as weight
    cntr, u, u0, d, jm, p, fpc, membership = cfuzzy.cmeans_coordinate(coordinate.T, CLUSTER_NUM, MAX_KTH, location_frequency, e=ERROR, algorithm="kthCluster_LocationFrequency")
    for i, key in enumerate(locations.keys()):
        setattr(locations[key], "cluster", membership[i])
        setattr(locations[key], "membership", numpy.atleast_2d(u[:,i]))

    cpygmaps.output_clusters(\
        [(float(x.lat), float(x.lng), str(x.cluster) + " >> " + x.lname + " >>u:" + str(u[x.cluster, i])) for i, x in enumerate(locations.values())], \
        membership, CLUSTER_NUM, OUTPUT_MAP)

    ccluster.output_location_cluster(locations.values(), "cluster", OUTPUT_CLUSTER)

    print("--------------------------------------")
    print("ENDTIME:", (datetime.datetime.now()))
    print("--------------------------------------")

    return users, locations

if __name__ == '__main__':
    main()