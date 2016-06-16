#ifndef ISIS_NEXUS_STREAMER_MOCKEVENTSUBSCRIBER_H
#define ISIS_NEXUS_STREAMER_MOCKEVENTSUBSCRIBER_H

#include "EventSubscriber.h"
#include <gmock/gmock.h>

class MockEventSubscriber : public EventSubscriber {
public:
  MOCK_METHOD2(setUp,
  void(const std::string &broker, const std::string &topic));
};

#endif //ISIS_NEXUS_STREAMER_MOCKEVENTSUBSCRIBER_H
