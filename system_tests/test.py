from __future__ import print_function
import os
import test_utils
import sys
from git import Repo
import time
import argparse

"""
Launch with:
python test.py /path/to/test/data [-p]
The "-p" flag executes on the physical cluster rather than launching virtual machines
"""


def check_all_received(producer_process_output, consumer_process_output):
    # Check the output from the consumer (consumer_process.output)
    # Did all messages and frames arrive?
    try:
        producer_frames = producer_process_output.split("Frames sent: ", 1)[1].split('\n', 1)[0]
        producer_bytes = producer_process_output.split("Bytes sent: ", 1)[1].split('\n', 1)[0]
        consumer_frames = consumer_process_output.split("Frames received: ", 1)[1].split('\n', 1)[0]
        consumer_bytes = consumer_process_output.split("Bytes received: ", 1)[1].split('\n', 1)[0]

        if producer_frames != consumer_frames:
            print("FAIL " + producer_frames + " frames sent but " + consumer_frames + " frames received")
            raise IndexError("")
        elif producer_bytes != consumer_bytes:
            print("FAIL " + producer_bytes + " bytes sent but " + consumer_bytes + " bytes received")
            raise IndexError("")
        else:
            print("PASS " + producer_frames + " frames sent and " + consumer_frames + " frames received.")
            print(producer_bytes + " bytes sent and " + consumer_bytes + " bytes received.")
    except IndexError:
        print("Unexpected output from producer or consumer, try running unit tests")
        sys.exit()


def get_single_metric(jmxhosts):
    print("Collecting metrics from broker...")
    with test_utils.cd("system_tests"):
        # Wait 90 seconds, then get the average rates from last minute
        time.sleep(90)
        for host in jmxhosts:
            jmx = test_utils.JmxMetrics(host)
            print(jmx.get_metric("BrokerTopicMetrics", "BytesInPerSec", "OneMinuteRate"))
    print("...done collecting metrics.")


def main():
    parser = argparse.ArgumentParser(description='Run system tests.')
    parser.add_argument('data_path', type=str,
                        help='the full path of the test data directory')
    parser.add_argument('-p', action='store_true',
                        help='use p flag to stream data across physical cluster instead of virtual cluster')
    parser.add_argument('-j', '--jmxport', type=str, default="9990",
                        help='specify the port on the broker for jmx')
    parser.add_argument('-g', '--producer_only', action='store_true',
                        help='use g flag to launch the producer but not consumer')
    args = parser.parse_args()

    # Redirect stdout to a system test output file
    # sys.stdout = open('system_test_output.txt', 'w')

    topic_name = "topic_system_test"
    broker = "localhost"
    jmxhosts = ["localhost:9990", "localhost:9991", "localhost:9992"]
    # datafile = "SANS_test.nxs"
    datafile = "WISH00034509_uncompressed.hdf5"

    repo_dir = "ansible-kafka-centos"
    # Clone git repository
    # if already exists in build director make sure up-to-date by pulling master
    if not args.p:
        try:
            Repo.clone_from("https://github.com/ScreamingUdder/ansible-kafka-centos.git", repo_dir)
        except:
            virtual_cluster_repo = Repo(repo_dir)
            origin = virtual_cluster_repo.remotes['origin']
            origin.pull()
        print("Starting up the virtual cluster...")
    else:
        print("Using real cluster")
        repo_dir = ""
        broker = "sakura"
        jmxhosts = ["sakura:" + args.jmxport, "hinata:" + args.jmxport]

    # Get kafka

    # Start up the virtual cluster
    with test_utils.Cluster(repo_dir):
        build_dir = os.path.join(os.getcwd())

        print("Start collecting metrics from broker...")
        jmxtool_broker = test_utils.JmxTool(build_dir, jmxhosts[1], topic=topic_name)
        jmxtool_cpu = test_utils.JmxTool(build_dir, jmxhosts[1], metrics="cpu")
        #jmxtool_memory = test_utils.JmxTool(build_dir, jmxhosts[1], metrics="memory")

        # Start the stopwatch
        t0 = time.time()

        # Launch the consumer
        if not args.producer_only:
            print("Launching consumer...", end="")
            consumer_process = test_utils.Subprocess(
                [os.path.join(build_dir, "nexus_consumer", "main_nexusSubscriber"),
                 "-b", broker,
                 "-t", topic_name,
                 "-q"])
            print(" done.")

        time.sleep(2)

        # Run the producer
        print("Launching producer...", end="")
        producer_process = test_utils.Subprocess(
            [os.path.join(build_dir, "nexus_producer", "main_nexusPublisher"),
             "-f", os.path.join(args.data_path, datafile),
             "-b", broker,
             "-t", topic_name,
             "-m", "100",
             "-q"])
        print(" done.")

        get_single_metric(jmxhosts)

        # Wait for the consumer subprocess to complete
        if not args.producer_only:
            print("Waiting for consumer to finish...")
            consumer_process.wait()
            print("...consumer process completed.")

        # Make sure the producer also finished
        print("Checking producer has finished...")
        producer_process.wait()
        print("...producer process completed.")

        # Stop the stopwatch
        t1 = time.time()
        total_time = t1 - t0
        print("Total time taken to send and receive all event data is " + str(total_time) + " seconds")

        # Finish collecting metrics
        # TODO plot metrics rather than print them
        print("Output from JmxTool:")
        print(jmxtool_broker.get_output())
        print(jmxtool_cpu.get_output())
        #print(jmxtool_memory.get_output())

        if not args.producer_only:
            check_all_received(producer_process.output, consumer_process.output)

        # Shut down the virtual cluster
        print("Shutting down virtual cluster...")

    print("...virtual cluster is down.")

    print("End of system tests")


if __name__ == "__main__":
    main()
