# Image compression
#
# You'll need Python 3 and the netpbm library, but netpbm is provided
# with the assignment code.    You can run this *only* on PNM images,
# which the netpbm library is used for.    You can also display a PNM
# image using the netpbm library as, for example:
#
#     python netpbm.py images/cortex.pnm
#
# The NumPy library should be installed and used for its faster array
# manipulation.  DO NOT USE NUMPY OTHER THAN TO CREATE AND ACCESS
# ARRAYS.  DOING SO WILL LOSE MARKS.


import sys, os, math, time, struct, netpbm
import numpy as np


# Text at the beginning of the compressed file, to identify the codec
# and codec version.

headerText = 'my compressed image - v1.0'


# Compress an image


def compress( inputFile, outputFile ):

    # Read the input file into a numpy array of 8-bit values
    #
    # The img.shape is a 3-type with rows,columns,channels, where
    # channels is the number of component in each pixel.  The
    # img.dtype is 'uint8', meaning that each component is an 8-bit
    # unsigned integer.

    img = netpbm.imread( inputFile ).astype('uint8')
    
    # Compress the image
    #
    # REPLACE THIS WITH YOUR OWN CODE TO FILL THE 'outputBytes' ARRAY.
    #
    # Note that single-channel images will have a 'shape' with only two
    # components: the y dimensions and the x dimension.    So you will
    # have to detect this and set the number of channels accordingly.
    # Furthermore, single-channel images must be indexed as img[y,x]
    # instead of img[y,x,1].  You'll need two pieces of similar code:
    # one piece for the single-channel case and one piece for the
    # multi-channel (R,G,B) case.
    #
    # You will build up bytes-strings of 16-bit integers during the
    # encoding.  To convert a 16-bit integer, i, to a byte-string, use
    #
    #   struct.pack('>h', i)
    #
    # where '>' means big-endian and 'h' means 2-byte signed integer.
    # If you know that the integers are unsigned, you should instead
    # use '>H'.
    #
    # Use these byte-strings (and concatenations of these byte-strings
    # when you have multiple integers in sequence) as dictionary keys.
    # DO NOT USE ARRAYS OF INTEGERS AS DICTIONARY KEYS.  DOING SO WILL
    # LOSE MARKS.

    startTime = time.time()
 
    outputIndices = bytearray()

    #initialize empty dict for a channel's LZW encoding
    lzw_dict = {struct.pack('>h',i) : i + 255 for i in range(-255,256)}

    #initialize empty symbol sequence
    s = b''

    #flag for later output
    multi_channel = len(img.shape) == 3

    if multi_channel:
        
        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                for c in range(img.shape[2]):
                    #use predictive encoding to get difference from previous pixel byte

                    if c == 0:
                        if x == 0:
                            if y == 0:
                                #first pixel in the image
                                sym = struct.pack('>h', int(img[0,0,0]))
                            else:
                                #diff with pixel from last col of previous row and last channel
                                sym = struct.pack('>h', int(img[y,x,c]) - int(img[y-1,-1,-1]))
                        else:
                            #diff with pixel from previous col last channel
                            sym = struct.pack('>h', int(img[y,x,c]) - int(img[y,x-1,-1]))
                    else:
                        #diff with pixel in previous channel
                        sym = struct.pack('>h', int(img[y,x,c]) - int(img[y,x,c-1]))

                    #LZW encoding
                    if (s+sym) in lzw_dict:
                        s += sym
                    else:
                        outputIndices += struct.pack('>H', lzw_dict[s])
                        if len(lzw_dict) < 65536:
                            lzw_dict[s+sym] = len(lzw_dict)
                        s = sym
            
        outputIndices += struct.pack('>H', lzw_dict[s])

                    
    else:
        #there is a single channel
            
        for y in range(img.shape[0]):
            for x in range(img.shape[1]):
                #use predictive encoding to get difference from previous pixel byte
                
                if x == 0:
                    if y == 0:
                        #no previous pixel so use original value
                        sym = struct.pack('>h', int(img[y,x]))
                    else:
                    #use difference between current and previous pixel
                    sym = struct.pack('>h', int(img[y,x]) - int(img[y-1,-1]))
                else:
                    #diff with pixel from previous col
                    sym = struct.pack('>h', int(img[y,x]) - int(img[y,x-1]))

                #LZW encoding
                if (s+sym) in lzw_dict:
                    s += sym
                else:
                    outputIndices += struct.pack('>H', lzw_dict[s])
                    if len(lzw_dict) < 65536:
                        lzw_dict[s+sym] = len(lzw_dict)
                    s = sym
        
        outputIndices += struct.pack('>H', lzw_dict[s])

    #encode the final index list
    #outputIndices = str(outputIndices).encode()

    endTime = time.time()

    # Output the bytes
    #
    # Include the 'headerText' to identify the type of file.    Include
    # the rows, columns, channels so that the image shape can be
    # reconstructed.

    outputFile.write( ('%s\n' % headerText).encode() )
    if multi_channel:
        outputFile.write( ('%d %d %d\n' % (img.shape[0], img.shape[1], img.shape[2])).encode() )
    else:
        outputFile.write( ('%d %d %d\n' % (img.shape[0], img.shape[1], 1)).encode() )
    outputFile.write( outputIndices )

    # Print information about the compression

    if multi_channel:
        inSize  = img.shape[0] * img.shape[1] * img.shape[2]
    else:
        inSize = img.shape[0] * img.shape[1]
    outSize = len(outputIndices)

    sys.stderr.write( 'Input size:         %d bytes\n' % inSize )
    sys.stderr.write( 'Output size:        %d bytes\n' % outSize )
    sys.stderr.write( 'Compression factor: %.2f\n' % (inSize/float(outSize)) )
    sys.stderr.write( 'Compression time:   %.2f seconds\n' % (endTime - startTime) )
    


# Uncompress an image

def uncompress( inputFile, outputFile ):

    # Check that it's a known file

    if inputFile.readline().decode() != headerText + '\n':
        sys.stderr.write( "Input is not in the '%s' format.\n" % headerText )
        sys.exit(1)
        
    # Read the rows, columns, and channels.    

    rows, columns, numChannels = [ int(x) for x in inputFile.readline().decode().split() ]

    # Read the raw bytes.

    inputBytes = bytearray(inputFile.read())

    # Build the image
    #
    # REPLACE THIS WITH YOUR OWN CODE TO CONVERT THE 'inputBytes'
    # ARRAY INTO AN IMAGE IN 'img'.
    #
    # When unpacking an UNSIGNED 2-byte integer from the inputBytes
    # byte-string, use struct.unpack( '>H', inputBytes[i:i+1] ) for
    # the unsigned integer in indices i and i+1.

    startTime = time.time()

    streamSize = rows*columns*numChannels
    inputIndices = [struct.unpack('>H', inputBytes[i:i+2])[0] for i in range(0,len(inputBytes),2)]

    img = np.empty([rows,columns,numChannels], dtype=np.uint8)


    decode_dict = {i : struct.pack('>h', i-255) for i in range(511)}

    s = decode_dict[inputIndices[0]]

    #start building a list of pixels to add to output image
    img[0][0][0] = struct.unpack('>h', s)

    #pixel # in output image
    pN = 1

    for ndx in inputIndices[1:]:

        if ndx in decode_dict:
            t = decode_dict[ndx]
            decode_dict[len(decode_dict)] = s + t[0:2]
        else:
            t = s + s[0:2]
            decode_dict[len(decode_dict)] = t

        for i in range(0, len(t), 2):
            y = pN // (columns*numChannels)
            x = (pN - y*columns*numChannels) // numChannels
            c = pN % numChannels

            if x == 0:
                #start of a row, use a plain value
                img[y][x][c] = struct.unpack('>h',t[i:i+2])
            else:
                #otherwise, use previous value
                img[y][x][c] = None
                
        s = t
    
    for y in range(rows):
        for x in range(columns):
            for c in range(numChannels):

                #already got the first index
                if y == 0 and x == 0 and c == 0:
                    continue

                if ndx in decode_dict:
                    t = decode_dict[ndx]
                    decode_dict[len(decode_dict)] = s + t[0:2]
                else:
                    t = s + s[0:2]
                    decode_dict[len(decode_dict)] = t

                if y == 0:
                    #start of a column, use plain value
                    img[y][x][c] = struct.unpack('>h',t)
                s = t
                i+=1

    endTime = time.time()
    sys.stderr.write( 'Uncompression time %.2f seconds\n' % (endTime - startTime) )

    # Output the image

    netpbm.imsave( outputFile, img )


    
# The command line is 
#
#     main.py {flag} {input image filename} {output image filename}
#
# where {flag} is one of 'c' or 'u' for compress or uncompress and
# either filename can be '-' for standard input or standard output.


if len(sys.argv) < 4:
    sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
    sys.exit(1)

# Get input file
 
if sys.argv[2] == '-':
    inputFile = sys.stdin
else:
    try:
        inputFile = open( sys.argv[2], 'rb' )
    except:
        sys.stderr.write( "Could not open input file '%s'.\n" % sys.argv[2] )
        sys.exit(1)

# Get output file

if sys.argv[3] == '-':
    outputFile = sys.stdout
else:
    try:
        outputFile = open( sys.argv[3], 'wb' )
    except:
        sys.stderr.write( "Could not open output file '%s'.\n" % sys.argv[3] )
        sys.exit(1)

# Run the algorithm

if sys.argv[1] == 'c':
    compress( inputFile, outputFile )
elif sys.argv[1] == 'u':
    uncompress( inputFile, outputFile )
else:
    sys.stderr.write( 'Usage: main.py c|u {input image filename} {output image filename}\n' )
    sys.exit(1)
