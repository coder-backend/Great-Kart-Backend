from .models import Category

def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)


# def navfoot(request):
#     navfoot = NavFoot.objects.all()
#     footerhyperlink =FooterRegistrationHyperLink.objects.all()
#     aaccrememimg = AccreMemImges.objects.all()

#     return dict(navfoot=navfoot, footerhyperlink=footerhyperlink, aaccrememimg=accreMemImges)
# {%for nav in navfoot %}
#     {{foot.image_top}}

# {%for hyperlink in footerhyperlink%}
#     {{hyperlink.hyperlink}}
# class AccreMemImges():
#     image_accre_meme = models.ImageField(upload_to="...")

# class FooterRegistrationHyperLink():
#     title=models.TextFeild(max_length=500)
#     hyperlink =models.TextFeild(max_length=500)

# class NavFoot(models.Model):
#     image_top = models.ImageField(upload_to="...")
#     book_a_consulattion_hyperlink = models.TextFeild(max_length=500)
#     occupation_hyperlink = models.TextFeild(max_length=500)
#     accredentation_member_Title = models.CharFeild(max_length=100)
#     image_nepal=models.ImageField(upload_to="...")
#     image_australia=models.ImageField(upload_to="...")
#     face_nepal=models.TextFeild(max_length=500)
#     insta_nepl=models.TextFeild(max_length=500)
#     face_aus=models.TextFeild(max_length=500)
#     insta_aus=models.TextFeild(max_length=500)
#     nepal_address=models.TextFeild(max_length=500)
#     aust=models.TextFeild(max_length=500)
#     connect_with_us=models.TextFeild(max_length=500)

