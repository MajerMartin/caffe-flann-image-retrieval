# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import img_search

x = img_search.distance_matrix.ImageSearchDistanceMatrix()

# vytvorit objekt, reprezentujici "vyhledavac" pres distance matrix

class ImageSearchDistanceMatrix(object):
     def __init__(self, max_images=100000, thumbnail_size=(150,150,3)):
         self.max_images = max_images
         self.thumbnail_size = thumbnail_size
         self.distance_matrix = None
         self.images = []
         self.features = []   
            
     def add_images(self, images, features):
          # features - do teto metody vstupuji jiz zvolene typy priznaku
          # images - zmensit dle self.thumbnail_size, fixni velikost      
          pass
            
     def find_k_nearest_by_index(self, img_index, k=3):
          pass
            
     def get_images(self, indexes):
          pass
            
     def save(self, filename):
          # ulozit do H5, klice images, features, max_images, thumbnail_size, distance_matrix (ulozit jen spodni trojuhelnik)
          pass      
            
     def load(self, filename):
          pass      
            
class ImageSearchKDTree(object):
     def __init__(self, max_images=100000):
         self.max_images = max_images
         self.distance_matrix = None
         self.images = []
         self.features = []   
            
     def add_images(self, images, features):
          pass
            
     def find_k_nearest_by_index(self, img_index, k=3):
          pass
            
     def get_images(self, indexes):
          pass
            
# zmerit rychlost pridavani obrazk a hledani nejblizsich            

