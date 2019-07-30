import io
import os
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
import math
from google.oauth2 import service_account

#Set application credentials for API. Will not be needed unless multiple credentials are loaded
#the curent credentials were hard coded into terminal
credentials = service_account.Credentials.from_service_account_file('/Users/ian/Documents/Capstone/credentials/google.json')
client = vision.ImageAnnotatorClient(credentials=credentials)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="/Users/ian/Documents/Capstone/credentials/google.json"



def google_vis(image_location):

    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname('/Users/ian/Documents/Capstone/images2/'),
        image_location)

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    ############################################
    # Performs label detection on the image file
    ############################################

    response = client.label_detection(image=image)
    labels = response.label_annotations

    label_list = []
    for label in labels:
        label_list.append(label.description)

    # Reads the text on the images
    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    read_text = []
    out_vertices = 0
    for text in texts[1:]:
        read_text.append(text.description)
#     calculates the vertices of the text location
        out_vertices += (abs(text.bounding_poly.vertices[0].x - text.bounding_poly.vertices[1].x) 
        * abs(text.bounding_poly.vertices[0].y - text.bounding_poly.vertices[2].y))/(300*250)


    ######################################
    # pulls out color profiles from images
    ######################################

    response = client.image_properties(image=image)
    props = response.image_properties_annotation

    color_dict = {}

    #option 1: store the color used no matter what shade as long as it represents over 5% of the image
    # for color in props.dominant_colors.colors:
    #     if (color.pixel_fraction) > .05:
    #         color_dict = {
    #           "red": (color.color.red),
    #           "green": (color.color.green),
    #           "blue": (color.color.blue),
    #           "alpha": (color.color.alpha),
    #           "fraction": (color.pixel_fraction)
    #             }

    #option 2: rounds the color to one of 20 colors and then stores the percentage to a dict


    master_color = {'red':(255, 0, 0), 'green':(0, 255, 0), 'yellow':(255, 255, 0), 'blue':(0, 0, 255), 'orange':(255, 160, 0), 'cyan':(0, 255, 255), 'magenta':(255, 0, 255), 'brown':(165,42,42), 'white':(255, 255, 255), 'black':(0, 0, 0)}             
    
    percent_color = {'red':0, 'green':0, 'yellow':0, 'blue':0, 'orange':0, 'cyan':0, 'magenta':0, 'brown':0, 'white':0, 'black':0}


    color_list =[]
    for color in props.dominant_colors.colors:
        color_list.append(color.score)
    color_denominator = sum(color_list)
    for color in props.dominant_colors.colors:
        point = (color.color.red), (color.color.green), (color.color.blue),
        colors = list(master_color.values())
        closest_colors = sorted(colors, key=lambda color: distance(color, point))
        closest_color = closest_colors[0]
        code = list(master_color.keys())[list(master_color.values()).index(closest_color)]
        percent_color[code] += (color.score / color_denominator)


    ######################################
    # Web detection
    ######################################

    # temporarily removing this module because Im not sure what to do with it

    # sample output:

    # web_entities {
    #   entity_id: "/m/0mgkg"
    #   score: 0.3331499993801117
    #   description: "Amazon.com"
    # }
    # web_entities {
    #   entity_id: "/m/0dwx7"
    #   score: 0.3202400505542755
    #   description: "Logo"
    # }
    # web_entities {
    #   entity_id: "/m/01cd9"
    #   score: 0.3095629811286926
    #   description: "Brand"
    # }
    # web_entities {
    #   entity_id: "/m/02m96"
    #   score: 0.27090001106262207
    #   description: "E-commerce"
    # }
    # web_entities {
    #   entity_id: "/m/03gq5hm"
    #   score: 0.2663790285587311
    #   description: "Font"
    # }
    # web_entities {
    #   entity_id: "/m/01jwgf"
    #   score: 0.23919999599456787
    #   description: "Product"
    # }
    # web_entities {
    #   entity_id: "/m/0191f8"
    #   score: 0.23784933984279633
    #   description: "Learning"
    # import argparse

    # image = types.Image(content=content)
    # web_detection = client.web_detection(image=image).web_detection

    # print(web_detection)
    
    ######################################
    # Facial Recognition
    ######################################  

    """Detects faces in an image."""
    response = client.face_detection(image=image)
    faces = response.face_annotations
    
    if faces:
        vertices = 1
    else:
        vertices = 0

    return (percent_color, read_text, out_vertices, vertices)

    # Names of likelihood from google.cloud.vision.enums
#     likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
#                        'LIKELY', 'VERY_LIKELY')
#     print('Faces:')

#     for face in faces:
#         print('anger: {}'.format(likelihood_name[face.anger_likelihood]))
#         print('joy: {}'.format(likelihood_name[face.joy_likelihood]))
#         print('surprise: {}'.format(likelihood_name[face.surprise_likelihood]))

#         vertices = (['({},{})'.format(vertex.x, vertex.y)
#                     for vertex in face.bounding_poly.vertices])

#         print('face bounds: {}'.format(','.join(vertices)))
     
    

def distance(c1, c2):
    (r1,g1,b1) = c1
    (r2,g2,b2) = c2
    return math.sqrt((r1 - r2)**2 + (g1 - g2) ** 2 + (b1 - b2) **2)