# Constantes do jogo convertidas para o pygame
# 170cm -> 600pixels, 130cm -> 520 pixels
CM_TO_PIXEL = 4
M_TO_PIXEL = 400
MAX_ROBOTS_NUMBER = 3
FIELD_DIMENSIONS = (170*CM_TO_PIXEL, 130*CM_TO_PIXEL)
ROBOT_DIMENSIONS =  (7.5*CM_TO_PIXEL, 7.5*CM_TO_PIXEL)
BALL_RADIUS = int(2.135*CM_TO_PIXEL)


def centralField2pygameAxisCoordinate(xy_tuple):
    return (int(xy_tuple[0]+FIELD_DIMENSIONS[0]/2), -int(xy_tuple[1]-FIELD_DIMENSIONS[1]/2))

def pygame2centralFieldAxisCoordinate(xy_tuple):
    return ((xy_tuple[0]-FIELD_DIMENSIONS[0]/2)/M_TO_PIXEL, (-xy_tuple[1]+FIELD_DIMENSIONS[1]/2)/M_TO_PIXEL)
