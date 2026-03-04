## dlna

A UPnP/DLNA client, support local file and online resource cast to screen.

**Support Online Resource.**

Thanks for nanodlna!


### Release Note
* 0.2.2: Fixed some tips.
* 0.2: Fixed multiple scans of the same.
* 0.1.7: Fixed an error caused by custom xml attributes.
* 0.1.6: Timeout expanded to 10s.
* 0.1.5: Optimize the tips content.
* 0.1.4:
    * Now you can select device by name.
    * Add 'How to use'
    * Fix bugs.
* 0.1.3: Fix bugs.


### How to use
* scan DLNA-enabled devices
```shell
>>> dlna device
```

* resource cast to screen
```shell
>>> dlna play "your_link_or_path"
```

* select device by url
```shell
>>> dlna play "your_link_or_path" -d "your_device_url"

# device url like 'http://host:port/'
```

* select device by name
```shell
>>> dlna play "your_link_or_path" -q "your_device_name"

# device name like 'room tv'
```