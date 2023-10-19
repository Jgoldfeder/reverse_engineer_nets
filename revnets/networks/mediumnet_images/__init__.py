from revnets.networks.mediumnet_images import mediumnet, mediumnet_small


def get_all_networks():
    return mediumnet, mediumnet_small


def get_networks():
    return mediumnet, mediumnet_small
