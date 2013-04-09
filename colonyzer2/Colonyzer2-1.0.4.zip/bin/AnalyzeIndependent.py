from Colonyzer2 import *

start=time.time()

(fullpath,outputimages,outputdata)=setupDirectories()
InsData=readInstructions(fullpath)

imList=getImageNames(outputimages,outputdata,fullpath)

while len(imList)>0:
    imName=imList[0]
    print(imName)
    imRoot=imName.split(".")[0]
    
    # Indicate that imName is currently being analysed, to allow parallel analysis
    tmp=open(os.path.join(outputdata,imRoot+".dat"),"w")
    tmp.close()

    # Get image and pixel array
    im,arrN=openImage(imName)

    # If we have ColonyzerParametryzer output for this filename, use it for initial culture location estimates
    if imName in InsData:
        (candx,candy,dx,dy)=SetUp(InsData[imName])
    else:
        (candx,candy,dx,dy)=SetUp(InsData['default'])

    # Automatically generate guesses for gridded array locations
    #(candx,candy,dx,dy)=estimateLocations(arrN,nx,ny,diam,showPlt=False)

    # Update guesses and initialise locations data frame
    locations=locateCultures(candx,candy,dx,dy,arrN)

    # Trim outer part of image to remove plate walls
    trimmed_arr=arrN[max(0,min(locations.y)-dy):min(arrN.shape[0],(max(locations.y)+dy)),max(0,(min(locations.x)-dx)):min(arrN.shape[1],(max(locations.x)+dx))]
    (thresh,bindat)=automaticThreshold(trimmed_arr)

    print("Markov")
    # Cutout thresholded pixels and fill with Markov field
    (finalMask,arrN)=makeMask(arrN,thresh,9999999999)   
    print("correction map")
    # Smooth (pseudo-)empty image 
    arr=numpy.copy(arrN)
    (correction_map,average_back)=makeCorrectionMap(arr0,locations)

    # Correct spatial gradient
    arr=arr*correction_map
    # Correct lighting differences
    locations=measureSizeAndColour(locations,arr,finalMask,average_back,imRoot,imRoot)

    # Write results to file
    locations.to_csv(os.path.join(outputdata,imRoot+".out"),"\t",index=False)
    dataf=saveColonyzer(os.path.join(outputdata,imRoot+".dat"),locations,thresh,dx,dy)

    # Visual check of culture locations
    imthresh=threshPreview(arr,thresh1,locations)
    imthresh.save(os.path.join(outputimages,imRoot+".png"))

    # Get ready for next image
    print("Finished: "+str(time.time()-start)+" s")
    imList=getImageNames(outputimages,outputdata,fullpath)
print("No more images to analyse... I'm done.")
