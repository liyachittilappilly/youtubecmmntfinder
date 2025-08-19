

# YouTube Comment Finder

A Python application that retrieves comments from a YouTube video and allows you to search for comments by a specific username (with fuzzy matching support).

## Features

- Extract comments from any YouTube video
- Fuzzy username matching (finds similar usernames even if not exact)
- Adjustable matching threshold for more control
- Handles both top-level comments and replies
- Normalizes text to handle accents, case differences, and extra spaces
- Provides detailed feedback about matched usernames

## Requirements

- Python 3.6+
- Google API Key (YouTube Data API v3)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/youtube-comment-finder.git
   cd youtube-comment-finder
   ```

2. Install the required packages:
   ```bash
   pip install google-api-python-client
   ```

## Getting a YouTube Data API Key

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the "YouTube Data API v3" for your project
4. Create credentials (API key)
5. (Recommended) Restrict your API key:
   - Set application restrictions to "IP addresses" and add your IP
   - Set API restrictions to "YouTube Data API v3" only
6. Copy your API key for use in the application

## Usage

1. Run the application:
   ```bash
   python youtube_comment_finder.py
   ```

2. Follow the prompts:
   - Enter your YouTube Data API key
   - Enter the YouTube video URL
   - Enter the username you want to search for (doesn't need to be exact)
   - Enter a matching threshold (0.1-0.9, default=0.6)

3. View the results:
   - The application will display all comments from usernames similar to your input
   - It will show which usernames were matched to your input

### Example

```
YouTube Comment Finder
----------------------
Enter your YouTube Data API key: [your-api-key]

Enter the YouTube video URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ

Fetching comments... (this may take a while for videos with many comments)

Found 1250 comments in the video.

Enter the username to find comments for: john smith
Enter matching threshold (0.1-0.9, default=0.6): 0.6

Found 5 comments from 2 similar usernames:
Matched usernames: John Smith, JohnnySmith

Comment #1:
Author: John Smith (matched to your input)
Published: 2023-01-15T12:30:45Z
Likes: 42
Text: Great video! I learned a lot from this.

Comment #2:
Author: JohnnySmith (matched to your input)
Published: 2023-01-16T08:15:22Z
Likes: 15
Text: I disagree with some points but overall good content.
```

## How Fuzzy Matching Works

The application uses fuzzy matching to find usernames similar to your input:

1. Text normalization removes accents, converts to lowercase, and normalizes spaces
2. The `difflib.get_close_matches` algorithm finds similar strings
3. The matching threshold controls how strict the matching is:
   - Higher values (e.g., 0.8) require closer matches
   - Lower values (e.g., 0.4) will find more distant matches
   - Default is 0.6, which works well for most cases

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This project uses the YouTube Data API but is not endorsed or certified by YouTube. All YouTube content is the property of their respective owners. Please respect YouTube's Terms of Service and API usage policies when using this application.
