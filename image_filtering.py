##### Importación de librería y funciones #####
from scipy.ndimage import imread
from scipy.misc import imsave
from scipy.fftpack import fft2, ifft2, fftshift
from math import pi
import numpy as np
import matplotlib.pyplot as plt

########## Definición de Funciones ############

# Obtiene la imagen que se encuentra en la ruta especificada (en escala de grises).
# 
# Entrada:
#	path	- Ruta donde se encuentra la imagen (incluyendo el nombre de la imagen), si 
#			esta en el mismo directorio que el programa, solo es el nombre del archivo.
#
# Salida:
#	imagen	- Matriz de pixeles, en otras palabras, la imagen (en escala de grises).
def read_image(path):
	imagen = imread(path,flatten = True)
	return imagen

# Guarda una imagen o un grafico de fft como imagen con el nombre especificado.
# 
# Entrada:
#	image		- Datos de la imagen que es guardada.
#	name 		- Nombre del archivo que se guarda.
#	transform	- Indica si la imagen a guardar es una imagen (matriz de pixeles) o
#				una transformada de fourier 2d de una imagen (transform = True). 
#
def save_image(image, name, transform = False):
	if transform != True:
		imsave(name,image,'png')
	else:		
		real = np.log(np.abs(image)+1)
		(height,width) = real.shape
		plt.figure(figsize=(10,10*height/width),facecolor='white')
		plt.clf()
		plt.title(name, fontsize = 28)
		plt.rc('text',usetex=False)
		plt.xlabel(r'$\omega_1$',fontsize=18)
		plt.ylabel(r'$\omega_2$',fontsize=18)
		plt.xticks(fontsize=16)
		plt.yticks(fontsize=16)
		plt.imshow( real, cmap='Greys_r',extent=[-pi,pi,-pi,pi],aspect='auto')
		plt.savefig(name)


# Normaliza una matriz de pixeles en escala de grises (imagen) a valores entre 0 y 1.
# Se usa para que los kernels funcionen correctamente.
# 
# Entrada:
#	image 	- Imagen sin normalizar (matriz de pixeles).
#
# Salida:
#	normalizedImage	- Imagen normalizada.
def normalize_image(image):
	return image / 255


# Soluciona el problema de que se obtiene una imagen mas pequeña que la original al
# aplicar el kernel en una imagen, esta funcion retorna la imagen original con un nuevo
# borde donde cada pixel es la media de la imagen (Retorna una imagen un poco mas grande).
# 
# Entrada:
#	image 	- Imagen a la que se le extiende el borde.
#	offset 	- Cantidad de pixeles que se debe extender cada borde de la imagen.
#			Es el tamaño de algun kernel nxn dividido en 2 (n/2), con aproximacion floor().
#
# Salida:
#	newImage	- Imagen con el borde extendido donde cada pixel del nuevo borde es el valor
#				medio de la imagen.
def fix_bounds(image, offset):
	n, m = image.shape
	average = image.mean()
	newImage = np.full((n + 2*offset, m + 2*offset), average)
	for i in range(0, n):
		for j in range(0, m):
			newImage[i + offset, j + offset] = image[i, j]

	return newImage

# Funcion que realiza la transformada de fourier en 2 dimensiones para una imagen.
# 
# Entrada:
#	image	- Imagen (matriz de pixeles) a la que se la aplica la transformada.
#
# Salida:
#	imageTransformation	- Transformada de fourier de la imagen.
def ftransform(image):
	imageTransformation = fft2(image, axes = (0,0))
	imageTransformation = fftshift(imageTransformation)
	return imageTransformation

# Convolucion en 2D entre una imagen (matriz de pixeles) y un filtro (kernel).
# 
# Entrada:
#	origin_signal	- Señal original, es la imagen obtenida por read_image().
#	kernel 			- Filtro que se le aplica a la señal (matriz nxn).
#
# Salida:
#	 g			- Matriz del tamaño de origin_signal con la imagen filtrada por el kernel.
def convolve_2D(origin_signal, kernel):
	print("Aplicando filtro...")
	# Asumiendo kernel cuadrados
	n,m = kernel.shape
	# Este offset indica la cantidad de pixeles extra que necesita la imagen para 
	# soportar las características del kernel
	offset = int(n/2)

	#Se ajustan los bordes de la señal original de acuerdo al offset
	origin_signal = fix_bounds(origin_signal, offset)


	r,s = origin_signal.shape
	#Matriz para soportar resultado de la convolución a lo largo de la señal original
	g = np.zeros((r - 2*offset, s - 2*offset))
	for k in range(0+offset,r-offset):
		for l in range(0+offset,s-offset):
			for i in range(0,n):
				for j in range(0,m):
					kOff = k - offset
					lOff = l - offset
					g[kOff,lOff] = g[kOff,lOff] + origin_signal[kOff+i,lOff+j]*kernel[i,j]

	print("Filtrado finalizado")
	return g

# Procesa la imagen que se encuentra en la ruta especificada, calculando y guardando lo siguiente:
#	La imagen filtrada por un kernel suavizador gaussiano (convolucion 2d)
#	La imagen filtrada por un kernel detector de bordes (convolucion 2d)
#	La transformada de fourier en 2 dimensiones de la imagen original (fft 2d)
#	La transformada de fourier en 2 dimensiones de la imagen suavizada (fft 2d)
#	La transformada de fourier en 2 dimensiones de la imagen con detector de bordes (fft 2d)
# 
# Entrada:
#	path - Ruta de la imagen a ser procesada.
#
def process_image(path):
	image = read_image(path)
	image = normalize_image(image)

	#Transformadada de fourier de señal original
	original_fft = ftransform(image)
	save_image(original_fft, "original_fft", transform = True)

	#Transformadada de fourier  inversa de señal orginal transformada
	#original_ifft = iftransform(original_fft)
	#save_image(original_ifft, "original_ifft")
	
	# Filtros a utilizar
	kernel_boundary_detector= np.asarray([[1, 2, 0, -2, -1]] * 5)
	kernel_gauss = (1/256)*np.asarray([[1,4,6,4,1],[4,16,24,16,4],[6,24,36,24,6],[4,16,24,16,4],[1,4,6,4,1]])

	# Transformada de fourier de los filtros
	fft_boundary_detector = ftransform(kernel_boundary_detector)
	fft_gauss = ftransform(kernel_gauss)

	save_image(fft_boundary_detector, "fft_boundary_detector", transform = True)
	save_image(fft_gauss, "fft_gauss", transform = True)

	#Aplicación de convolución
	result_gauss = convolve_2D(image,kernel_gauss)
	result_boundary = convolve_2D(image,kernel_boundary_detector)
	save_image(result_gauss,"gauss", transform = False)
	save_image(result_boundary,"boundary", transform = False)

	#Aplicación de transformada de fourier de dos dimensiones
	gauss_fft = ftransform(result_gauss)
	boundary_fft = ftransform(result_boundary)
	save_image(gauss_fft,"gauss_fft", transform = True)
	save_image(boundary_fft, "boundary_fft", transform = True)

	#Transformadada de fourier  inversa de señal con gauss transformada
	#gauss_ifft = iftransform(gauss_fft)
	#save_image(gauss_ifft, "gauss_ifft")

	#Transformadada de fourier  inversa de señal con boundary transformada
	#boundary_ifft = iftransform(boundary_fft)
	#save_image(boundary_ifft, "boundary_ifft")


################ Bloque Main ##################

##PROCESAMIENTO	
process_image("leena512.bmp")

