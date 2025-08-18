import googleapiclient.discovery
import googleapiclient.errors
import re
from urllib.parse import urlparse, parse_qs
from difflib import get_close_matches
import unicodedata

def normalize_text(text):
    """Normalize text for comparison by removing accents and converting to lowercase"""
    # Remove accents
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Convert to lowercase and remove extra spaces
    return re.sub(r'\s+', ' ', text.lower().strip())

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

def find_similar_usernames(comments, input_username, threshold=0.6):
    """Find usernames similar to the input using fuzzy matching"""
    # Get all unique usernames
    all_usernames = list(set(comment['author'] for comment in comments))
    
    # Normalize input username
    normalized_input = normalize_text(input_username)
    
    # Create normalized version of all usernames
    normalized_usernames = [normalize_text(username) for username in all_usernames]
    
    # Find close matches
    close_matches = get_close_matches(
        normalized_input, 
        normalized_usernames, 
        n=10,  # Maximum number of matches to return
        cutoff=threshold
    )
    
    # Map back to original usernames
    similar_usernames = []
    for match in close_matches:
        # Find original username that matches this normalized version
        for i, norm_username in enumerate(normalized_usernames):
            if norm_username == match:
                similar_usernames.append(all_usernames[i])
                break
    
    return similar_usernames

def find_user_comments(comments, username, threshold=0.6):
    """Filter comments by usernames similar to the input"""
    similar_usernames = find_similar_usernames(comments, username, threshold)
    
    if not similar_usernames:
        return []
    
    # Get comments from any of the similar usernames
    user_comments = []
    for comment in comments:
        if comment['author'] in similar_usernames:
            user_comments.append({
                'comment': comment,
                'matched_username': comment['author']
            })
    
    return user_comments

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
    
    # Ask for matching threshold
    try:
        threshold = float(input("Enter matching threshold (0.1-0.9, default=0.6): ").strip() or "0.6")
        threshold = max(0.1, min(0.9, threshold))  # Clamp between 0.1 and 0.9
    except ValueError:
        print("Invalid threshold, using default 0.6")
        threshold = 0.6
    
    user_comments = find_user_comments(comments, username, threshold)
    
    # Display results
    if user_comments:
        # Get unique matched usernames
        matched_usernames = list(set(item['matched_username'] for item in user_comments))
        print(f"\nFound {len(user_comments)} comments from {len(matched_usernames)} similar usernames:")
        print(f"Matched usernames: {', '.join(matched_usernames)}\n")
        
        for i, item in enumerate(user_comments, 1):
            comment = item['comment']
            print(f"Comment #{i}:")
            print(f"Author: {comment['author']} (matched to your input)")
            print(f"Published: {comment['published_at']}")
            print(f"Likes: {comment['like_count']}")
            print(f"Text: {comment['text']}\n")
    else:
        # Try to find similar usernames even if no comments found
        similar_usernames = find_similar_usernames(comments, username, threshold)
        if similar_usernames:
            print(f"\nNo comments found, but found these similar usernames: {', '.join(similar_usernames)}")
            print("Try adjusting the threshold or check if these users commented in this video.")
        else:
            print(f"\nNo comments found and no usernames similar to '{username}' with threshold {threshold}.")
            print("Try lowering the threshold or check the spelling.")

if __name__ == "__main__":
    main()