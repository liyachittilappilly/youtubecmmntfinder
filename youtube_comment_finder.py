import googleapiclient.discovery
import googleapiclient.errors
import re
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    parsed_url = urlparse(url)
    if parsed_url.netloc == 'www.youtube.com' and parsed_url.path == '/watch':
        return parse_qs(parsed_url.query)['v'][0]
    elif parsed_url.netloc == 'youtu.be':
        return parsed_url.path[1:]
    else:
        raise ValueError("Invalid YouTube URL format")

def get_youtube_comments(api_key, video_id):
    """Fetch all comments from a YouTube video"""
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    
    comments = []
    next_page_token = None
    
    try:
        while True:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token,
                textFormat="plainText"
            )
            response = request.execute()
            
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'like_count': comment['likeCount'],
                    'published_at': comment['publishedAt']
                })
                
                # Check for replies
                if item['snippet']['totalReplyCount'] > 0:
                    reply_request = youtube.comments().list(
                        part="snippet",
                        parentId=item['id'],
                        maxResults=100,
                        textFormat="plainText"
                    )
                    reply_response = reply_request.execute()
                    
                    for reply_item in reply_response['items']:
                        reply = reply_item['snippet']
                        comments.append({
                            'author': reply['authorDisplayName'],
                            'text': reply['textDisplay'],
                            'like_count': reply['likeCount'],
                            'published_at': reply['publishedAt']
                        })
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
    except googleapiclient.errors.HttpError as e:
        print(f"An HTTP error occurred: {e}")
        return None
    
    return comments

def find_user_comments(comments, username):
    """Filter comments by username"""
    return [comment for comment in comments if comment['author'].lower() == username.lower()]

def main():
    print("YouTube Comment Finder")
    print("----------------------")
    
    # Get API key (in production, use environment variables or config files)
    api_key = input("Enter your YouTube Data API key: ").strip()
    
    # Get YouTube video URL
    video_url = input("\nEnter the YouTube video URL: ").strip()
    try:
        video_id = get_video_id(video_url)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Fetch comments
    print("\nFetching comments... (this may take a while for videos with many comments)")
    comments = get_youtube_comments(api_key, video_id)
    if comments is None:
        print("Failed to retrieve comments.")
        return
    
    print(f"\nFound {len(comments)} comments in the video.")
    
    # Get username and find comments
    username = input("\nEnter the username to find comments for: ").strip()
    user_comments = find_user_comments(comments, username)
    
    # Display results
    if user_comments:
        print(f"\nFound {len(user_comments)} comments by {username}:\n")
        for i, comment in enumerate(user_comments, 1):
            print(f"Comment #{i}:")
            print(f"Author: {comment['author']}")
            print(f"Published: {comment['published_at']}")
            print(f"Likes: {comment['like_count']}")
            print(f"Text: {comment['text']}\n")
    else:
        print(f"\nNo comments found by {username} in this video.")

if __name__ == "__main__":
    main()