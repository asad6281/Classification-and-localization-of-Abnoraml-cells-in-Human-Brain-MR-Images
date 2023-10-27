import tkinter
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
import os
import numpy as np
import ctypes

from FE_ResNet50Functions_stnd1 import getModel, PredictAbnormality
from FE_ResUnetFunctions_stnd1 import getModel_ResUnet, Localize_Abnormality

#Specifies a unique application-defined Application User Model ID (AppUserModelID) that identifies the current process to the taskbar. 
#This identifier allows an application to group its associated processes and windows under a single taskbar button.
myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

model_resnet50 = getModel()
model_ResUnet = getModel_ResUnet()

top = tkinter.Tk()
top.config(bg="white")
width = top.winfo_screenwidth()
height = top.winfo_screenheight()
print(width, height)
top.geometry( str(width) + "x" + str(height) + "+0+0")
top.title("Quantification and Localization of Abnormal Brain Cells in Human Brain MR Images")
small_icon = tkinter.PhotoImage(file="FrontEndIconsDefaultImages\icons8-brain-16.png")
large_icon = tkinter.PhotoImage(file="FrontEndIconsDefaultImages\icons8-brain-32.png")
top.iconphoto(False, large_icon, small_icon)

imgSmallmain = Image.open( "FrontEndIconsDefaultImages\Black Background.tif" )
WIDTH, HEIGHT = imgSmallmain.size
imgLargemain = imgSmallmain.resize( (int(WIDTH*2), int(HEIGHT*2) ), Image.Resampling.LANCZOS )
Bg = ImageTk.PhotoImage( imgLargemain )

def inputImage():
    folder_path = tkinter.StringVar()
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    if filename:
        read = True
    else:
        read = False
    
    if read:    
        global ImageList
        global ImageList_currentIndex
        global ImageList_length
        global CurrentDirectory_list
        global ImageNames
        global DataPreview
        global img_lb
        global dir_lb
        global Preview_ReverseButton
        global Preview_ForwardButton  

        # DECLARE Variables as lists, Index variable initialized to zero...
        ImageList_currentIndex = 0
        ImageList = []
        image_list_sorted = []
        ImageNames = []
        image_name_sorted = []
        CurrentDirectory_list = []
        curr_dir_list_sorted = []
        
        DataPreview.grid_forget()
        DataPreview = tkinter.LabelFrame(homeFrame, bg="gray99", padx=10, pady=10, text="Data Preview", font=( "Calibre", 10, "bold") )
        dir_lb = tkinter.Label(DataPreview, bg="gray99", text="Filename: "+" | Slice Number: ", font=("Calibre", 10), bd=1, relief="sunken")
        img_lb = tkinter.Label(DataPreview, image=Bg )

        DataPreview.grid(row=0, column=1, sticky='w,e,n,s')
        dir_lb.grid(row=0, column=0, columnspan=2, sticky='w,e')
        img_lb.grid(row=1, column=0, columnspan=2)

        # Iterate directory to get number of images
        number = 0.0
        for path in os.listdir(filename):
            number += 1.0
        barIncrement = 100/number

        # Progress bar Declared... | Placed on Window
        InputProgress = ttk.Progressbar(DataPreview, orient="horizontal", mode="determinate", length=100 )
        InputProgress.grid(row=3, column=0, columnspan=2, sticky='w,e')

        # READ Images using Image Name and Directory combined...
        max_len = 0
        min_len = 99
        for img_names in os.listdir(filename):
            imgSmall = Image.open( os.path.join(filename,img_names) )
            WIDTH, HEIGHT = imgSmall.size
            imgLarge = imgSmall.resize( (int(WIDTH*2), int(HEIGHT*2)), Image.Resampling.LANCZOS )
            img = ImageTk.PhotoImage( imgLarge )

            if img is not None:
                ImageList.append(img)
                ImageNames.append(img_names)
                CurrentDirectory_list.append( os.path.join(filename,img_names) )

                if len(img_names) > max_len:
                    max_len = len(img_names)

                if len(img_names) < min_len:
                    min_len = len(img_names)
                    
            InputProgress['value'] += barIncrement
            top.update_idletasks()

        # Sort the lists: Image Name, Image, Current Directroy...
        for k in range(min_len, max_len + 1):
            for j in range( 0, len(ImageNames) ):
                if len(ImageNames[j]) == k:
                    image_name_sorted.append(ImageNames[j])
                    image_list_sorted.append(ImageList[j])
                    curr_dir_list_sorted.append(CurrentDirectory_list[j])
                    
        ImageNames = image_name_sorted
        ImageList = image_list_sorted
        CurrentDirectory_list = curr_dir_list_sorted
        ImageList_length = len(ImageList)

        # DELETE previous Preview Label...
        DataPreview.grid_forget()

        # Widgets Declared...
        DataPreview = tkinter.LabelFrame(homeFrame, bg="gray99", padx=10, pady=10, text="Data Preview", font=("Calibre", 10, "bold") )
        dir_lb = tkinter.Label(DataPreview, bg="gray99", text="Filename: "+ImageNames[0][0:-4]+" | Slice Number: "+str( ImageList_currentIndex+1 )+" of "+str(ImageList_length), font=("Calibre", 9), bd=1, relief="sunken")
        img_lb = tkinter.Label(DataPreview, image=(ImageList[0]), bd=1, relief="sunken")
        Preview_ReverseButton = tkinter.Button(DataPreview, text="  ", bg="gray98", width="25",state="disabled")
        Preview_ForwardButton = tkinter.Button(DataPreview, text=">>", activebackground="lightblue", bg="gray98", width="25", command=lambda: Preview_ForwardFunc(ImageList_currentIndex+1) )
        
        InitiateAnalysis = tkinter.Button(ActionsFrame, text="Analysis", activebackground="lightblue", font=("Calibre", 10), bg="gray98", width="20", pady=3, command=Analysis)

        # Widgets placed on Window, Updated...
        DataPreview.grid(row=0, column=1, sticky="n,s")
        dir_lb.grid(row=0, column=0, columnspan=2, sticky='w,e')
        img_lb.grid(row=1, column=0, columnspan=2)
        Preview_ReverseButton.grid(row=2, column=0, pady=5, stick='e')
        Preview_ForwardButton.grid(row=2, column=1, pady=5, sticky='w')
        
        InitiateAnalysis.grid(row=1, column=0, pady=5)
    

def Preview_ForwardFunc(ImageList_currentIndex):
    global ImageList
    global ImageNames
    global DataPreview
    global img_lb
    global dir_lb
    global Preview_ReverseButton
    global Preview_ForwardButton
    
    # DELETE previous Preview...
    DataPreview.grid_forget()
    
    #FRAME Declared...
    DataPreview = tkinter.LabelFrame(homeFrame, bg="gray99", padx=10, pady=10, text="Data Preview", font=("Calibre", 10, "bold") )
    
    # LABELS Declared...
    dir_lb = tkinter.Label(DataPreview, bg="gray99", text="Filename: "+ImageNames[ImageList_currentIndex][0:-4]+" | Slice Number: "+str( ImageList_currentIndex+1 )+" of "+str(ImageList_length), font=("Calibre", 9), bd=1, relief="sunken")
    img_lb = tkinter.Label(DataPreview, image=(ImageList[ImageList_currentIndex]) )
    
    # BUTTONS Declared...
    Preview_ReverseButton = tkinter.Button(DataPreview, text="<<", activebackground="lightblue", bg="gray98", width="25", command=lambda: Preview_ReverseFunc(ImageList_currentIndex-1) )
    Preview_ForwardButton = tkinter.Button(DataPreview, text=">>", activebackground="lightblue", bg="gray98", width="25", command=lambda: Preview_ForwardFunc(ImageList_currentIndex+1) )
    
    if ImageList_currentIndex == ImageList_length-1:
        Preview_ForwardButton = tkinter.Button(DataPreview, text="  ", bg="gray98", width="25", state="disabled")
    
    # FRAME placed on Window, Updated...
    DataPreview.grid(row=0, column=1, sticky="n,s")
    
    # LABELS placed on Window, Updated...
    dir_lb.grid(row=0, column=0, columnspan=2, sticky='w,e')
    img_lb.grid(row=1, column=0, columnspan=2)
    
    # BUTTONS placed on Window Updated...
    Preview_ReverseButton.grid(row=2, column=0, pady=5, sticky='e')
    Preview_ForwardButton.grid(row=2, column=1, pady=5, sticky='w')
    

def Preview_ReverseFunc(ImageList_currentIndex):
    global ImageList
    global ImageNames
    global DataPreview
    global img_lb
    global dir_lb
    global Preview_ReverseButton
    global Preview_ForwardButton
    
    # DELETED previous Preview...
    DataPreview.grid_forget()
    
    # LABELS Declared...
    DataPreview = tkinter.LabelFrame(homeFrame, bg="gray99", padx=10, pady=10, text="Data Preview", font=("Calibre", 10, "bold") )
    
    # LABELS Declared...
    dir_lb = tkinter.Label(DataPreview, bg="gray99", text="Filename: "+ImageNames[ImageList_currentIndex][0:-4]+" | Slice Number: "+str( ImageList_currentIndex+1 )+" of "+str(ImageList_length), font=("Calibre", 9), bd=1, relief="sunken")
    img_lb = tkinter.Label(DataPreview, image=(ImageList[ImageList_currentIndex]) )
    
    # BUTTONS Declared...
    Preview_ReverseButton = tkinter.Button(DataPreview, text="<<", activebackground="lightblue", bg="gray98", width="25", command=lambda: Preview_ReverseFunc(ImageList_currentIndex-1) )
    Preview_ForwardButton = tkinter.Button(DataPreview, text=">>", activebackground="lightblue", bg="gray98", width="25", command=lambda: Preview_ForwardFunc(ImageList_currentIndex+1) )
    
    if ImageList_currentIndex == 0:
        Preview_ReverseButton = tkinter.Button(DataPreview, text="  ", bg="gray98", width="25", state="disabled")
    
    # FRAME placed on Window, Updated...
    DataPreview.grid(row=0, column=1, sticky="n,s")
    
    # LABELS placed on Window, Updated...
    dir_lb.grid(row=0, column=0, columnspan=2, sticky='w,e')
    img_lb.grid(row=1, column=0, columnspan=2)
    
    # BUTTONS placed on Window, Updated...
    Preview_ReverseButton.grid(row=2, column=0, pady=5, sticky='e')
    Preview_ForwardButton.grid(row=2, column=1, pady=5, sticky='w')
    
    
def Analysis():
    global AnalyzedImageNames
    global ImagesAnalyzed
    global OriginalIndex
    global AnalyzedImagesCount
    global ImageAnalysisResult
    global analyzed_dir_lb
    global analyzed_img_lb
    global backwardAnalysis
    global forwardAnalysis
    global AnalyzedImageIndex
    
    # VARIABLES Declared as lists, first variable initialized to zero...
    AnalyzedImageIndex = 0
    ImagesAnalyzed = []
    AnalyzedImageNames = []
    OriginalIndex = []
    imageId = []
    mask = []
    # DELETED previous Analysis Results...
    ImageAnalysisResult.grid_forget()
    
    # RECONSTRUCT Frame...
    ImageAnalysisResult = tkinter.LabelFrame(homeFrame, bg="gray99", padx=10, pady=10, text="Analysis Results", font=( "Calibre", 10, "bold") )
    analyzed_dir_lb = tkinter.Label(ImageAnalysisResult, bg="gray99", text="Filename: "+" | Slice Number: ", font=("Calibre", 10), bd=1, relief="sunken")
    analyzed_img_lb = tkinter.Label(ImageAnalysisResult, image=Bg )
    InitiateAnalysis = tkinter.Button(ActionsFrame, text="Analysis", font=("Calibre", 10), bg="grey98", width="20", pady=4, state="disabled")
    # REPLACE Frame...
    ImageAnalysisResult.grid(row=0, column=2, sticky='w,e,n,s')
    analyzed_dir_lb.grid(row=0, column=0, columnspan=2, sticky='w,e')
    analyzed_img_lb.grid(row=1, column=0, columnspan=2)
    InitiateAnalysis.grid(row=1, column=0, sticky="w,e")
    # Progress bar Declared | placed on Window, next task
    CLASSLOCQUANProgression = ttk.Progressbar(ImageAnalysisResult, orient="horizontal", mode="determinate", length=100 )
    CLASSLOCQUANProgression.grid(row=3, column=0, columnspan=2, sticky='w,e')
    
    # ANALYSIS - Predict Abnormality | Localize abnormality
    AnalyzedImageNames, OriginalIndex = PredictAbnormality(CurrentDirectory_list, model_resnet50, top, CLASSLOCQUANProgression)
    CLASSLOCQUANProgression['value'] = 0
    if AnalyzedImageNames:
        mask = Localize_Abnormality(AnalyzedImageNames, model_ResUnet, top, CLASSLOCQUANProgression)
    
    # READ Images through Directories in Analyzed Image Names...
    CLASSLOCQUANProgression['value'] = 0
    barIncrement=100/len(mask)
    count = 0
    for images in AnalyzedImageNames:
        CLASSLOCQUANProgression['value']+=barIncrement
        top.update_idletasks()
        imgSmall__ = Image.open( images )
        imgSmall_ = np.asarray(imgSmall__, dtype=np.uint8)
        imgSmall = imgSmall_.copy() 
        imgSmall.setflags(write=1)
        
        if mask[count] == 'No mask':
            continue
        else:
            # Round off and reshape predicted mask
            predictedMask = mask[count].squeeze().round()
        count+=1
        
        # QUANTIZE Abnormal Region, Numpy array used
        for i in range(0, 255):
            for j in range(0, 255):
                if predictedMask[i, j] == 1:
                    imgSmall[i, j, 0:] = (0, 255, 0)
        
        imgSmallImage = Image.fromarray(imgSmall.astype('uint8'), 'RGB')
        WIDTH, HEIGHT = imgSmallImage.size
        imgLarge = imgSmallImage.resize( (int(WIDTH*2), int(HEIGHT*2)), Image.Resampling.LANCZOS )
        img = ImageTk.PhotoImage( imgLarge )
        ImagesAnalyzed.append(img)
    
    AnalyzedImagesCount = len(ImagesAnalyzed)
    
    # NAMES extracted from original list: Image Name...
    for i in range(0, len(OriginalIndex) ):
        AnalyzedImageNames[i] = ImageNames[ OriginalIndex[i] ]
    
    InitiateAnalysis = tkinter.Button(ActionsFrame, text="Analysis", font=("Calibre", 10), bg="grey98", width="20", pady=4, state="disabled")
    # DELETED previous Analysis Results...
    ImageAnalysisResult.grid_forget()
    
    # FRAMES Declared...
    ImageAnalysisResult = tkinter.LabelFrame(homeFrame, bg="gray99", padx=10, pady=10, text="Analysis Results", font=("Calibre", 10, "bold") )
    
    # LABELS Declared...
    analyzed_dir_lb = tkinter.Label(ImageAnalysisResult, bg="gray99", text="Filename: "+AnalyzedImageNames[0][0:-4]+" | Slice Number: "+str( AnalyzedImageIndex+1 )+" of "+str(AnalyzedImagesCount), font=("Calibre", 10), bd=1, relief="sunken")
    analyzed_img_lb = tkinter.Label(ImageAnalysisResult, image=(ImagesAnalyzed[0]) )
    
    # BUTTONS Declared...
    backwardAnalysis = tkinter.Button(ImageAnalysisResult,text="  ", bg="gray98", width="25", state="disabled")
    forwardAnalysis = tkinter.Button(ImageAnalysisResult,text=">>",activebackground="lightblue",bg="gray98",width="25",command=lambda: forward_Analysis(AnalyzedImageIndex+1))
    
    # FRAME placed on Window, Updated...
    ImageAnalysisResult.grid(row=0,column=2)
    
    # LABELS placed on Windows, Updated...
    analyzed_dir_lb.grid(row=0,column=0, columnspan=2, sticky='w,e')
    analyzed_img_lb.grid(row=1,column=0, columnspan=2)
    
    # BUTTONS placed on Window, Updated...
    backwardAnalysis.grid(row=2, column=0, pady=5, sticky='e')
    forwardAnalysis.grid(row=2, column=1, pady=5, sticky='w')
    InitiateAnalysis.grid(row=1, column=0)
    

def forward_Analysis(AnalyzedImageIndex):
    global AnalyzedImageNames
    global ImagesAnalyzed
    global ImageAnalysisResult
    global analyzed_dir_lb
    global analyzed_img_lb
    global backwardAnalysis
    global forwardAnalysis
    
    # DELETED previous Analysis Results...
    ImageAnalysisResult.grid_forget()
    
    # FRAMES Declared...
    ImageAnalysisResult = tkinter.LabelFrame(homeFrame, bg="gray99", padx=10, pady=10, text="Analysis Results", font=("Calibre", 10, "bold") )
    
    # LABELS Declared...
    analyzed_dir_lb = tkinter.Label(ImageAnalysisResult, bg="gray99", text="Filename: "+AnalyzedImageNames[AnalyzedImageIndex][0:-4]+" | Slice Number: "+str( AnalyzedImageIndex+1 )+" of "+str(AnalyzedImagesCount), font=("Calibre", 10), bd=1, relief="sunken")
    analyzed_img_lb = tkinter.Label(ImageAnalysisResult, image=(ImagesAnalyzed[AnalyzedImageIndex]) )
    
    # BUTTONS Declared...
    backwardAnalysis = tkinter.Button(ImageAnalysisResult,text="<<",activebackground="lightblue", bg="gray98", width="25", command=lambda: backward_Analysis(AnalyzedImageIndex-1) )
    forwardAnalysis = tkinter.Button(ImageAnalysisResult,text=">>",activebackground="lightblue",bg="gray98",width="25",command=lambda: forward_Analysis(AnalyzedImageIndex+1) )
    
    if AnalyzedImageIndex == AnalyzedImagesCount-1:
        forwardAnalysis = tkinter.Button(ImageAnalysisResult,text="  ",bg="white",width="25", state="disabled")
    
    # FRAME placed on Window, Updated...
    ImageAnalysisResult.grid(row=0,column=2)
    
    # LABELS placed on Windows, Updated...
    analyzed_dir_lb.grid(row=0,column=0, columnspan=2, sticky='w,e')
    analyzed_img_lb.grid(row=1,column=0, columnspan=2)
    
    # BUTTONS placed on Window, Updated...
    backwardAnalysis.grid(row=2, column=0, pady=5, sticky='e')
    forwardAnalysis.grid(row=2, column=1, pady=5, sticky='w')
    

def backward_Analysis(AnalyzedImageIndex):
    global AnalyzedImageNames
    global ImagesAnalyzed
    global ImageAnalysisResult
    global analyzed_dir_lb
    global analyzed_img_lb
    global backwardAnalysis
    global forwardAnalysis
    
    # DELETED previous Analysis Results...
    ImageAnalysisResult.grid_forget()
    
    # FRAMES Declared...
    ImageAnalysisResult = tkinter.LabelFrame(homeFrame, bg="gray99", padx=10, pady=10, text="Analysis Results", font=("Calibre", 10, "bold") )
    
    # LABELS Declared...
    analyzed_dir_lb = tkinter.Label(ImageAnalysisResult, bg="gray99", text="Filename: "+AnalyzedImageNames[AnalyzedImageIndex][0:-4]+" | Slice Number: "+str( AnalyzedImageIndex+1 )+" of "+str(AnalyzedImagesCount), font=("Calibre", 10), bd=1, relief="sunken")
    analyzed_img_lb = tkinter.Label(ImageAnalysisResult, image=(ImagesAnalyzed[AnalyzedImageIndex]) )
    
    # BUTTONS Declared...
    backwardAnalysis = tkinter.Button(ImageAnalysisResult,text="<<",activebackground="lightblue", bg="gray98", width="25", command=lambda: backward_Analysis(AnalyzedImageIndex-1) )
    forwardAnalysis = tkinter.Button(ImageAnalysisResult,text=">>",activebackground="lightblue",bg="gray98",width="25",command=lambda: forward_Analysis(AnalyzedImageIndex+1) )
    
    if AnalyzedImageIndex == 0:
        backwardAnalysis = tkinter.Button(ImageAnalysisResult, text="  ", bg="white",width="25", state="disabled")
    
    # FRAME placed on Window, Updated...
    ImageAnalysisResult.grid(row=0,column=2)
    
    # LABELS placed on Windows, Updated...
    analyzed_dir_lb.grid(row=0,column=0, columnspan=2, sticky='w,e')
    analyzed_img_lb.grid(row=1,column=0, columnspan=2)
    
    # BUTTONS placed on Window, Updated...
    backwardAnalysis.grid(row=2, column=0, pady=5, sticky='e')
    forwardAnalysis.grid(row=2, column=1, pady=5, sticky='w')


def main():
    global homeFrame
    global ActionsFrame
    global DataPreview
    global ImageAnalysisResult
    
    # FRAMES Declared...
    homeFrame=tkinter.LabelFrame(top,bg="gray100",padx=5,pady=5 )
    ActionsFrame = tkinter.LabelFrame(homeFrame, bg="gray99", padx=10, pady=10, text="Actions", font=( "Calibre", 10, "bold") )
    DataPreview = tkinter.LabelFrame(homeFrame, bg="gray99", padx=10, pady=10, text="Data Preview", font=( "Calibre", 10, "bold") )
    ImageAnalysisResult = tkinter.LabelFrame(homeFrame, bg="gray99", padx=10, pady=10, text="Analysis Results", font=( "Calibre", 10, "bold") )
    
    # BUTTONS Declared...
    InputImage = tkinter.Button(ActionsFrame, text="Input Image", font=("Calibre", 10), activebackground="lightblue",bg="gray98",width="20",pady=3, command=inputImage )
    InitiateAnalysis = tkinter.Button(ActionsFrame, text="Analysis", font=("Calibre", 10), bg="gray98", width="20", pady=3, state="disabled")
    
    # LABELS Declared...
    dir_lb = tkinter.Label(DataPreview, bg="gray99", text="Filename: "+" | Slice Number: ", font=("Calibre", 10), bd=1, relief="sunken")
    img_lb = tkinter.Label(DataPreview, image=Bg )
    analyzed_dir_lb = tkinter.Label(ImageAnalysisResult, bg="gray99", text="Filename: "+" | Slice Number: ", font=("Calibre", 10), bd=1, relief="sunken")
    analyzed_img_lb = tkinter.Label(ImageAnalysisResult, image=Bg )

    # FRAMES Placed on Window
    homeFrame.grid(row=0, column=0, sticky='w,e,n,s')
    ActionsFrame.grid(row=0, column=0, sticky='w,e,n,s')
    DataPreview.grid(row=0, column=1, sticky='w,e,n,s')
    ImageAnalysisResult.grid(row=0, column=2, sticky='w,e,n,s')

    # BUTTONS Placed on Window
    # Options
    InputImage.grid(row=0, column=0, pady=5)
    InitiateAnalysis.grid(row=1, column=0, pady=5)

    # LABELS Placed on Window
    dir_lb.grid(row=0, column=0, columnspan=2, sticky='w,e')
    img_lb.grid(row=1, column=0, columnspan=2)
    analyzed_dir_lb.grid(row=0, column=0, columnspan=2, sticky='w,e')
    analyzed_img_lb.grid(row=1, column=0, columnspan=2)

    top.mainloop()

if __name__ == "__main__":
    main()