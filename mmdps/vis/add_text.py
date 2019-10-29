from PIL import Image, ImageDraw, ImageFont

def add_title_BNV(imagePath, text, font_size = 72):
	img = Image.open(imagePath)
	newImg = Image.new('RGBA', (img.width, img.height+font_size), (255, 255, 255, 255))
	newImg.paste(img, (0, font_size, img.width, img.height+font_size))
	draw = ImageDraw.Draw(newImg)
	font = ImageFont.truetype('arial.ttf', font_size)
	w, h = draw.textsize(text, font = font)
	draw.text((img.width/2-w/2, 0), text, (0, 0, 0), font = font)
	newpng = imagePath[:imagePath.rfind('.')] + '_decorated.png'
	newImg.save(newpng)

def add_text(imagePath, text):
	img = Image.open(imagePath)
	newImg = Image.new('RGBA', (img.width, img.height), (255, 255, 255, 255))
	newImg.paste(img, (0, 0, img.width, img.height))
	draw = ImageDraw.Draw(newImg)
	font = ImageFont.truetype('arial.ttf', 24)
	w, h = draw.textsize(text, font = font)
	draw.text((img.width/2-w/2, 0), text, (0, 0, 0), font = font)
	newpng = imagePath[:imagePath.rfind('.')] + '_decorated.png'
	newImg.save(newpng)
