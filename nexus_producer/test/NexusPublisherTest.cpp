#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <memory>

#include "EventDataTestHelper.h"
#include "MockEventPublisher.h"
#include "NexusPublisher.h"

using ::testing::AtLeast;
using ::testing::_;

class NexusPublisherTest : public ::testing::Test {};

TEST(NexusPublisherTest, test_create_streamer) {
  extern std::string testDataPath;

  const std::string broker = "broker_name";
  const std::string topic = "topic_name";

  auto publisher = std::make_shared<MockEventPublisher>();
  EXPECT_CALL(*publisher.get(), setUp(broker, topic)).Times(AtLeast(1));

  NexusPublisher streamer(publisher, broker, topic,
                         testDataPath + "SANS_test.nxs");
}

TEST(NexusPublisherTest, test_create_message_data) {
  extern std::string testDataPath;

  const std::string broker = "broker_name";
  const std::string topic = "topic_name";

  auto publisher = std::make_shared<MockEventPublisher>();

  EXPECT_CALL(*publisher.get(), setUp(broker, topic)).Times(AtLeast(1));

  NexusPublisher streamer(publisher, broker, topic,
                         testDataPath + "SANS_test.nxs");
  auto eventData = streamer.createMessageData(static_cast<hsize_t>(0));

  std::string rawbuf;
  eventData->getBufferPointer(rawbuf);

  auto testHelper =
      EventDataTestHelper(reinterpret_cast<const uint8_t *>(rawbuf.c_str()));
  EXPECT_EQ(794, testHelper.getCount());
}

TEST(NexusPublisherTest, test_stream_data) {

  extern std::string testDataPath;

  const std::string broker = "broker_name";
  const std::string topic = "topic_name";

  auto publisher = std::make_shared<MockEventPublisher>();

  EXPECT_CALL(*publisher.get(), setUp(broker, topic)).Times(1);
  EXPECT_CALL(*publisher.get(), sendMessage(_, _))
      .Times(static_cast<int>(18131));

  NexusPublisher streamer(publisher, broker, topic,
                         testDataPath + "SANS_test.nxs");
  EXPECT_NO_THROW(streamer.streamData());
}