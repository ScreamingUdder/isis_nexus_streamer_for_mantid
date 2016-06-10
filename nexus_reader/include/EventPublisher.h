#ifndef ISIS_NEXUS_STREAMER_EVENTPUBLISHER_H
#define ISIS_NEXUS_STREAMER_EVENTPUBLISHER_H

#include <string>

class EventPublisher {
public:
  virtual ~EventPublisher() {}
  virtual void createConfiguration(const std::string &broker,
                                   const std::string &topic) = 0;
  virtual void sendMessage(char *buf, size_t bufSize) = 0;
};

#endif // ISIS_NEXUS_STREAMER_EVENTPUBLISHER_H
