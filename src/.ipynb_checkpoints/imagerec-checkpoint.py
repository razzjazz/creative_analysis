import io
import os
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
import math


def google_vis(image_location):
    #Set application credentials for API. Will not be needed unless multiple credentials are loaded
    #the curent credentials were hard coded into terminal

    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    # The name of the image file to annotate
    file_name = os.path.join(
        os.path.dirname('/Users/ian/Documents/week3/Capstone1/images/'),
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

    for text in texts:
        read_text.append(text.description)

#     calculates the vertices of the text location
        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])


        out_vertices = (','.join(vertices))


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


    master_color = {'red':(230, 25, 75), 'green':(60, 180, 75), 'yellow':(255, 225, 25), 'blue':(0, 130, 200), 'orange':(245, 130, 48), 'purple':(145, 30, 180), 'cyan':(70, 240, 240), 'magenta':(240, 50, 230), 'lime':(210, 245, 60), 'pink':(250, 190, 190), 'teal':(0, 128, 128), 'lavender':(230, 190, 255), 'brown':(170, 110, 40), 'beige':(255, 250, 200), 'maroon':(128, 0, 0), 'mint':(170, 255, 195), 'olive':(128, 128, 0), 'apricot':(255, 215, 180), 'navy':(0, 0, 128), 'grey':(128, 128, 128), 'white':(255, 255, 255), 'black':(0, 0, 0)}             
    percent_color = {'apricot': 0,
     'beige': 0,
     'black': 0,
     'blue': 0,
     'brown': 0,
     'cyan': 0,
     'green': 0,
     'grey': 0,
     'lavender': 0,
     'lime': 0,
     'magenta': 0,
     'maroon': 0,
     'mint': 0,
     'navy': 0,
     'olive': 0,
     'orange': 0,
     'pink': 0,
     'purple': 0,
     'red': 0,
     'teal': 0,
     'white': 0,
     'yellow': 0}


    for color in props.dominant_colors.colors:
        point = (color.color.red), (color.color.green), (color.color.blue),
        fraction = (color.pixel_fraction)
        colors = list(master_color.values())
        closest_colors = sorted(colors, key=lambda color: distance(color, point))
        closest_color = closest_colors[0]
        code = list(master_color.keys())[list(master_color.values()).index(closest_color)]
        percent_color[code] += fraction 


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

    return (percent_color, read_text, out_vertices, faces)

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