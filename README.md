## yt-dlp-proxy Guide

yt-dlp-proxy is a script designed to help you avoid throttling and bans by automatically selecting the best proxy for yt-dlp. 

#### Howto start with yt-dlp-proxy

```yt-dlp-proxy update```

This will also perform a speed test for each free proxy and select the best one available.

#### Download with yt-dlp-proxy
Use yt-dlp-proxy just like you would use yt-dlp! Pass all the arguments to yt-dlp-proxy instead.
Example:

```yt-dlp-proxy --format bv[vcodec^=avc!]+ba https://www.youtube.com/watch?v=bQB0_4BG-9F```

If the proxy becomes slow over time, rerun the command from Step 1 to refresh the proxy selection.

### Optional: Symlink and systemwide installation
Setting Up a Symlink for Easier Access

To make yt-dlp-proxy easier to access from anywhere, you can create a symlink in */usr/bin* or another directory in your system’s PATH.
___

**Option 1:** Create a Symlink in /usr/bin

Open a terminal.
Run the following command, replacing */path/to/yt-dlp-proxy* with the actual path to the yt-dlp-proxy script:

```sudo ln -s /path/to/yt-dlp-proxy /usr/bin/yt-dlp-proxy```

Now you can use yt-dlp-proxy from any directory in the terminal.
___

**Option 2:** Install to */usr/bin*

If you prefer, you can directly move the yt-dlp-proxy script to /usr/bin:

Open a terminal.
Run the following command, again replacing /path/to/yt-dlp-proxy with the path to the script:
    
```sudo install /path/to/yt-dlp-proxy /usr/bin/yt-dlp-proxy```

This will copy yt-dlp-proxy to /usr/bin, making it globally accessible.

Now, you can simply type yt-dlp-proxy from any location in the terminal to use the script.
___
