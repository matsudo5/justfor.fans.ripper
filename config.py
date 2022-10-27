overwrite_existing = False
save_path = r"G:\Rip"
save_full_text = True

# AVAILABLE FIELDS
#  name
#  post_date
#  post_id
#  desc
#  photo_seq (do not change this)
#  ext (do not change this)

file_name_format = '{photo_seq}_{post_date}.{ext}'

# PROBABLY DON'T NEED TO CHANGE THIS
api_url = 'https://justfor.fans/ajax/getPosts.php?UserID={userid}&Type=All&StartAt={seq}&Source=Home&UserHash4={hash}'
#https://justfor.fans/ajax/getPosts.php?Type=One&UserID=1678804&PosterID=789072&StartAt=0&Page=Profile&UserHash4=a300a46de96801ff5891aef195cfa12c&SplitTest=0