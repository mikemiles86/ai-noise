```python
import random

def word_jumble(message):
    words = message.lower().split()
    jumbled_words = [' '.join(random.sample(word, len(word))) for word in words]
    return ' '.join(jumbled_words)

message = "yodel goblet under saddle kettle mosaic ember ribbon jasmine folds weasel loud igloo quiver under melts glacier cactus sideways nectar eleven quiver pulley seventeen anchor mitten purple lagoon teapot bramble furnace loud orbit gadget ladder drizzle lantern loud noodle argues melts elbow harbor walnut quill meadow sings jasmine inkwell remembers blue violin vapor an"
print(word_jumble(message))
```

This program randomly jumbles the words in the input message.