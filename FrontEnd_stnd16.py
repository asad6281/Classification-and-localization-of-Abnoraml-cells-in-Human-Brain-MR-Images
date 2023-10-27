import tkinter
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image
import os
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import ctypes
import tensorflow as tf

from FE_ResNet50Functions_stnd1 import getModel, PredictAbnormality
from FE_ResUnetFunctions_stnd1 import getModel_ResUnet, Localize_Abnormality, metric_iou, tversky
from REPORT import generate_report
import cv2

myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
HistNMetric = False
CurrentDirectory = ""
keys = []
Analysis_complete = False
Report_Generated = False
message_l = ["",
             "Images successfully\nloaded, Initiate Analysis\nfor abnormality\ndetection and localization",
             "Images Analysis\ndetected abnormality",
             "Images Analysis\ndetected no abnormality"]
model_resnet50 = getModel()
model_ResUnet = getModel_ResUnet()
for i in range(0, 256):
    keys.append(i)


def generate(tktop, ab_status, image_list_index, image_list, image_names, image_list_len, hist_list, masktrue, maskpred):
    global Report_Generated
    global CurrentDirectory
    
    Report_Generated = True
    generate_report(image_names, CurrentDirectory)
    ConstructBase(tktop=tktop, initAnstate=False, histMetricstate=True, input_case=False, abnormality=ab_status, image_names=image_names, 
                  image_list=image_list, image_list_index=image_list_index, currentdirectory_list=None, hist_list=hist_list, image_list_len=image_list_len, 
                  masktrue=masktrue, maskpred=maskpred)
    

def HistMetricsDisplay(imagehistmetric, fgsz, ImageIndex, hist_list, Analysis, masktrue, maskpred):
    global HistNMetric
    global keys
    global CurrentDirectory
    
    if HistNMetric == False:
        HistNMetric=True
    else:
        HistNMetric=False 
    if Analysis and masktrue:
        message=' After Analysis'
        y_true = cv2.imread( os.path.join(CurrentDirectory, masktrue[ImageIndex]), cv2.IMREAD_GRAYSCALE )
        for i in range(0,255):
            for j in range(0,255):
                if y_true[i][j] == 255:
                    y_true[i][j] = 1.0
                elif y_true[i][j] == 0:
                    y_true[i][j] = 0.0
        iou = metric_iou(y_true, maskpred[ImageIndex])
        iou = round(iou*100, 2)
        tversky_res = tversky(y_true, maskpred[ImageIndex])
        tversky_res = round( tf.get_static_value(tversky_res, partial=False)*100, 2)
    elif Analysis:
        message=' After Analysis'
        iou = ""
        tversky_res=""
    else:
        message=' Before Analysis'
        iou = ""
        tversky_res=""
     
    if HistNMetric:
        imagehistmetric.grid_forget()
        if maskpred:
            width1 = 0.5
            HistIndex = (ImageIndex)*3
            Metric_lb = tkinter.Label(imagehistmetric, bg="gray97", font=("@Microsoft YaHei UI", 10), bd=1, relief="sunken", 
                                      text="Tversky:"+str(tversky_res)+" | IOU:"+str(iou) )
            plt.ylim(0,500)
            HistFig = plt.Figure(figsize=fgsz)
            plot = HistFig.gca()
            plot.bar(keys, hist_list[HistIndex], color = 'red', width=width1)
            plot.bar(keys, hist_list[HistIndex+1], color = 'green', width=width1)
            plot.bar(keys, hist_list[HistIndex+2], color = 'blue', width=width1)
            plot.set_title("slice number: "+str(ImageIndex+1)+message )

            Histogram_canvas = FigureCanvasTkAgg(HistFig, imagehistmetric)
            imagehistmetric.grid(row=0, column=2, sticky='w,e,n,s')
            Histogram_canvas.get_tk_widget().grid(row=1, column=0, columnspan=2)
            Metric_lb.grid(row=2, column=0, columnspan=2, pady=(0,0), sticky='w,e')
        else:
            width1 = 0.5
            HistIndex = (ImageIndex)*3
            Metric_lb = tkinter.Label(imagehistmetric, bg="gray97", font=("@Microsoft YaHei UI", 10), bd=1, relief="sunken", 
                                      text="Tversky:"+str(tversky_res)+" | IOU:"+str(iou) )

            HistFig = plt.Figure(figsize=fgsz)
            plot = HistFig.gca()
            plot.bar(keys, hist_list[HistIndex], color = 'red', width=width1)
            plot.bar(keys, hist_list[HistIndex+1], color = 'green', width=width1)
            plot.bar(keys, hist_list[HistIndex+2], color = 'blue', width=width1)
            plot.set_title("slice number: "+str(ImageIndex+1)+message )

            Histogram_canvas = FigureCanvasTkAgg(HistFig, imagehistmetric)
            imagehistmetric.grid(row=0, column=2, sticky='w,e,n,s')
            Histogram_canvas.get_tk_widget().grid(row=1, column=0, columnspan=2)
            Metric_lb.grid(row=2, column=0, columnspan=2, pady=(0,0), sticky='w,e')
    else:
        print(HistNMetric)
        imagehistmetric.grid_forget()
        HistFig = plt.Figure(figsize=fgsz)
        plot = HistFig.gca()
        
        Histogram_canvas = FigureCanvasTkAgg(HistFig, imagehistmetric)
        imagehistmetric.grid(row=0, column=2, sticky='w,e,n,s')
        Metric_lb = tkinter.Label(imagehistmetric, bg="gray97", font=("@Microsoft YaHei UI", 10), bd=1, relief="sunken", text="Tversky: | IOU:")
        Histogram_canvas.get_tk_widget().grid(row=1, column=0, columnspan=2)
        Metric_lb.grid(row=2, column=0, columnspan=2, pady=(0,0), sticky='w,e')
    top.update_idletasks()
        


def ConstructBase(tktop, initAnstate, histMetricstate, input_case, abnormality, image_names, image_list, image_list_index, currentdirectory_list, 
                  hist_list, image_list_len, masktrue, maskpred):
    global Bg
    global Analysis_complete
    global Report_Generated
    global message_l
    
    bgcolor = "gray99"
    butcolor = "gray98"
    labcolor = "gray97"
    
    image_display = []
    message = message_l[0]
    message_bg = labcolor
    fgsz = (5,6)
    
    if initAnstate:
        initAn='normal'
        message = message_l[1]
        message_bg = 'lawn green'
    else:
        initAn='disabled'
        message = message_l[0]
        message_bg = labcolor
    
    if histMetricstate:
        histMetric='normal'
    else:
        histMetric='disabled'
        
    if image_list_len!=0:
        image_display=image_list
    else:
        image_display.append(Bg)
    
    if image_list_len!=0:
        if image_list_index==0:
            bbut_state='disabled'
            bbut_text="  "
        else:
            bbut_state='normal'
            bbut_text="<<"
        if image_list_index==image_list_len-1:
            fbut_state='disabled'
            fbut_text="  "
        else:
            fbut_state='normal'
            fbut_text=">>"
    else:
        bbut_state='disabled'
        fbut_state='disabled'
        bbut_text="<<"
        fbut_text=">>"
    if image_names:
        name = str(image_names[image_list_index][0:-4])
        index = str(image_list_index+1)
        total = ' of '+str(image_list_len)
    else:
        name = ''
        index = ''
        total = ''
    if Analysis_complete:
        analysis_hist=True
        if abnormality:
            message = message_l[2]
            message_bg = 'firebrick1'
            if Report_Generated:
                genrep_state = 'disabled'
            else:
                genrep_state = 'normal'
        else:
            message = message_l[3]
            message_bg = 'lawn green'
            histMetric='disabled'
            if Report_Generated:
                genrep_state = 'disabled'
            else:
                genrep_state = 'normal'
    else:
        analysis_hist=False
        genrep_state = 'disabled'
    for item in tktop.winfo_children():
        item.grid_forget()
        item.destroy()
    homeFrame = tkinter.LabelFrame(tktop, bg=bgcolor,padx=0,pady=0 )
    ActionsFrame = tkinter.LabelFrame(homeFrame, bg=bgcolor, padx=0, pady=0 ) # gray99 --> midnight blue
    DataPreview = tkinter.LabelFrame(homeFrame, bg=bgcolor, padx=0, pady=0 )
    ImageHistMetric = tkinter.LabelFrame(homeFrame, bg=bgcolor, padx=0, pady=0 )
    homeFrame.pack()
    ActionsFrame.grid(row=0, column=0, padx=0, pady=0, sticky='n,s,e,w')
    DataPreview.grid(row=0, column=1, padx=0, pady=0, sticky='n,s,e,w')
    ImageHistMetric.grid(row=0, column=2, padx=0, pady=0, sticky='n,s,e,w')
    
    InputImage = tkinter.Button(ActionsFrame,text="INPUT IMAGE",font=("@Microsoft YaHei UI",8),activebackground="lightblue",bg=butcolor,width="22",pady=5,
                                command=lambda: inputImage(tktop))
    InitiateAnalysis=tkinter.Button(ActionsFrame,text="INITIATE ANALYSIS",activebackground="lightblue",font=("@Microsoft YaHei UI", 8),bg=butcolor,width="22",
                                    pady=5, 
                                    command=lambda: Analysis(tktop, image_list, image_names, image_list_len, hist_list, masktrue), state=initAn)
    HistMetricsBut = tkinter.Button(ActionsFrame, text="GENERATE HISTOGRAM", font=("@Microsoft YaHei UI", 8),activebackground="lightblue",bg=butcolor, 
                                    width="22", pady=5, 
                                    command=lambda: HistMetricsDisplay(ImageHistMetric, fgsz, image_list_index, hist_list, analysis_hist, masktrue, maskpred),
                                    state=histMetric)
    Generate_Report = tkinter.Button(ActionsFrame, text="GENERATE REPORT", activebackground="lightblue", font=("@Microsoft YaHei UI", 8),bg=butcolor, 
                                     width="22", pady=5,
                                     command=lambda: generate(tktop, abnormality, image_list_index, image_list, image_names, image_list_len, hist_list, 
                                                              masktrue, maskpred), state=genrep_state )
    Preview_ReverseButton = tkinter.Button(DataPreview, text=bbut_text, activebackground="lightblue", font=("@Microsoft YaHei UI", 8), bg=butcolor, width="25",
                                           command=lambda: Preview_ReverseFunc(tktop, image_list_index-1, abnormality, image_list, image_names, 
                                                                               image_list_len, hist_list, masktrue, maskpred)
                                           , state=bbut_state )
    Preview_ForwardButton = tkinter.Button(DataPreview, text=fbut_text, activebackground="lightblue", font=("@Microsoft YaHei UI", 8), bg=butcolor, width="25",
                                           command=lambda: Preview_ForwardFunc(tktop, image_list_index+1, abnormality, image_list, image_names, 
                                                                               image_list_len, hist_list, masktrue, maskpred)
                                           , state=fbut_state )
    InputImage.grid(row=0, column=0, padx=(0,1), pady=(0,1), stick='n,s')
    InitiateAnalysis.grid(row=1, column=0, padx=(0,1), pady=1, stick='n,s')
    HistMetricsBut.grid(row=2, column=0, padx=(0,1), pady=1, stick='n,s')
    Generate_Report.grid(row=3, column=0, padx=(0,1), pady=(1,0), stick='n,s')
    Preview_ReverseButton.grid(row=2, column=0, pady=0, stick='e,w')
    Preview_ForwardButton.grid(row=2, column=1, pady=0, sticky='e,w')
    
    HistFig = plt.Figure(figsize=fgsz)
    HistFig.patch.set_facecolor('w')
    plot = HistFig.gca()
    Histogram_canvas = FigureCanvasTkAgg(HistFig, ImageHistMetric)
    Metric_lb = tkinter.Label(ImageHistMetric, bg=labcolor, font=("@Microsoft YaHei UI", 10), bd=1, relief="sunken", text="Tversky: | IOU:")
    Histogram_canvas.get_tk_widget().grid(row=1, column=0)
    Metric_lb.grid(row=2, column=0, pady=(0,0), sticky='w,e')
    
    dir_lb = tkinter.Label(DataPreview,bg=labcolor,text="Filename: "+name+" | Slice Number: "+index+total, font=("@Microsoft YaHei UI",10), bd=1, 
                           relief="sunken")# 99->97
    img_lb = tkinter.Label(DataPreview, image=image_display[image_list_index], background=bgcolor )
    mes_lb = tkinter.Label(ActionsFrame,bg=message_bg, font=("@Microsoft YaHei UI", 8), text=message,bd=1,relief="sunken")
    img_lb.grid(row=0, column=0, columnspan=2)
    dir_lb.grid(row=1, column=0, columnspan=2, sticky='w,e')
    mes_lb.grid(row=4, column=0, sticky='w,e')
    top.update_idletasks()
    
    InputProgress = ttk.Progressbar(DataPreview, orient="horizontal", mode="determinate", length=100 )
    InputProgress.grid(row=3, column=0, columnspan=2, pady=(1,0), sticky='w,e')
    if input_case:
        return InputProgress


def Preview_ForwardFunc(tktop, image_list_index, ab_status, image_list, image_names, image_list_len, hist_list, masktrue, maskpred):
    global HistNMetric
    global Analysis_complete
    
    if HistNMetric:
        HistNMetric = False
        
    if Analysis_complete:
        initAnstate=False
    else:
        initAnstate=True
    top.update_idletasks()
    ConstructBase(tktop=tktop, initAnstate=initAnstate, histMetricstate=True, input_case=False, abnormality=ab_status, image_names=image_names, 
                  image_list=image_list, image_list_index=image_list_index, currentdirectory_list=None, hist_list=hist_list, image_list_len=image_list_len, 
                  masktrue=masktrue, maskpred=maskpred)


def Preview_ReverseFunc(tktop, image_list_index, ab_status, image_list, image_names, image_list_len, hist_list, masktrue, maskpred):
    global HistNMetric
    
    if HistNMetric:
        HistNMetric = False
    
    if Analysis_complete:
        initAnstate=False
    else:
        initAnstate=True
    top.update_idletasks()
    ConstructBase(tktop=tktop, initAnstate=initAnstate, histMetricstate=True, input_case=False, abnormality=ab_status, image_names=image_names, 
                  image_list=image_list, image_list_index=image_list_index, currentdirectory_list=None, hist_list=hist_list, image_list_len=image_list_len, 
                  masktrue=masktrue, maskpred=maskpred)
    

def inputImage(tktop):
    global CurrentDirectory
    global Analysis_complete
    global ratio_mult
    
    global Analysis_complete
    
    folder_path = tkinter.StringVar()
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    if filename:
        read = True
        CurrentDirectory = filename
    else:
        read = False
    Analysis_complete = False
    
    if read:    
        '''DECLARE Variables as lists, Index variable initialized to zero...'''
        ImageList = []
        image_list_sorted = []
        HistList = []
        HistList_sorted = []
        ImageNames = []
        image_name_sorted = []
        TruemaskNames = []
        True_mask_names_sorted = []
        ''' GET number, Images '''
        number = len( os.listdir(filename) )
        barIncrement = 100/number
        max_len = 0
        min_len = 99
        maskmax_len = 0
        maskmin_len = 99
        ''' PROGRESS BAR '''
        InputProgress = ConstructBase(tktop=tktop, initAnstate=False, histMetricstate=False, input_case=True, abnormality=False, image_names=None, 
                                      image_list=None, image_list_index=0, currentdirectory_list=None, hist_list=None, image_list_len=0, masktrue=None, 
                                      maskpred=None)
        ''' READ Images '''
        for img_names in os.listdir(filename):
            flag = img_names.find('mask')
            if flag==-1:
                mask_true = None
                imgSmall = Image.open(os.path.join(filename,img_names))
                imgSmall.convert('RGB')
                WIDTH, HEIGHT = imgSmall.size
                imgLarge = imgSmall.resize( (int((WIDTH*2.1)*ratio_mult),int( (HEIGHT*2.1)*ratio_mult)),Image.Resampling.LANCZOS)
                img = ImageTk.PhotoImage(imgLarge)
                r,g,b = imgSmall.split()
                hist_r = r.histogram() 
                hist_g = g.histogram() 
                hist_b = b.histogram()
            else:
                mask_true = img_names
                img = None
            if img is not None:
                ImageList.append(img)
                ImageNames.append(img_names)
                HistList.append(hist_r)
                HistList.append(hist_g)
                HistList.append(hist_b)
                if len(img_names) > max_len:
                    max_len = len(img_names)
                if len(img_names) < min_len:
                    min_len = len(img_names)
            if mask_true is not None:
                TruemaskNames.append(mask_true)
                if len(mask_true) > maskmax_len:
                    maskmax_len = len(mask_true)
                if len(mask_true) < maskmin_len:
                    maskmin_len = len(mask_true)
            InputProgress['value'] += barIncrement
            top.update_idletasks()
        ''' SORT ImageNames, ImageList, CurrentDirectroy_list, HistList '''
        for k in range(min_len, max_len + 1):
            for j in range(0, len(ImageNames) ):
                if len(ImageNames[j]) == k:
                    image_name_sorted.append(ImageNames[j])
                    image_list_sorted.append(ImageList[j])
                    l = j*3
                    HistList_sorted.append(HistList[l])
                    HistList_sorted.append(HistList[l+1])
                    HistList_sorted.append(HistList[l+2])
        for k in range(maskmin_len, maskmax_len + 1):
            for j in range(0, len(TruemaskNames) ):
                if len(TruemaskNames[j]) == k:
                    True_mask_names_sorted.append(TruemaskNames[j])
                    
        ImageNames = image_name_sorted
        ImageList = image_list_sorted
        HistList = HistList_sorted
        TruemaskNames = True_mask_names_sorted
        ImageList_length = len(ImageList)
        Analysis_complete = False
        ''' DELETE '''
        InputProgress.grid_forget()
        InputProgress.destroy()
        ConstructBase(tktop=tktop, initAnstate=True, histMetricstate=True, input_case=False, abnormality=False, image_names=ImageNames, image_list=ImageList, 
                      image_list_index=0, currentdirectory_list=CurrentDirectory, hist_list=HistList, image_list_len=ImageList_length, masktrue=TruemaskNames, 
                      maskpred=None)


def Analysis(tktop, image_list_org, image_names, image_list_len_org, hist_list_org, masktrue):
    global HistNMetric
    global CurrentDirectory
    global ratio_mult
    global keys
    
    global Analysis_complete
    global Report_Generated
    
    ''' VARIABLES Declared '''
    AnalyzedImagePaths = []
    OriginalIndex = []
    mask = []
    masktrueAn = []
    ImagesAnalyzed = []
    HistList_Analyzed = []
    maskpred = []
    truemask = []
    if HistNMetric:
        HistNMetric = False
    if Report_Generated == True:
            Report_Generated = False
    '''PROGRESS BAR '''
    CLASSLOCQUANProgression = ConstructBase(tktop=tktop, initAnstate=False, histMetricstate=False, input_case=True, abnormality=False, image_names=None, 
                                            image_list=None, image_list_index=0, currentdirectory_list=None, hist_list=None, image_list_len=0, 
                                            masktrue=masktrue, maskpred=None)
    ''' ANALYSIS - Predict Abnormality''' '''here'''
    AnalyzedImagePaths, OriginalIndex = PredictAbnormality(CurrentDirectory, image_names,  model_resnet50, tktop, CLASSLOCQUANProgression)
    CLASSLOCQUANProgression['value'] = 0
    if AnalyzedImagePaths:
        ''' ANALYSIS - Localize Abnormality '''
        mask = Localize_Abnormality(AnalyzedImagePaths, model_ResUnet, tktop, CLASSLOCQUANProgression)
        CLASSLOCQUANProgression['value'] = 0
        barIncrement=100/len(mask)
        count = 0
        for images in AnalyzedImagePaths:
            CLASSLOCQUANProgression['value']+=barIncrement
            top.update_idletasks()
            imgSmall__ = Image.open( images )
            imgSmall__.convert('RGB')
            imgSmall_ = np.asarray(imgSmall__, dtype=np.uint8)
            imgSmall = imgSmall_.copy() 
            imgSmall.setflags(write=1)
            if mask[count] == 'No mask':
                continue
            else:
                predictedMask = mask[count].squeeze().round()
                maskpred.append(predictedMask)
            count+=1
            '''image corresponding to mask initialized as copy of image'''
            ImgCorrMask = imgSmall_.copy()
            ''' QUANTIZE - VISUAL '''
            for i in range(0, 255):
                for j in range(0, 255):
                    if predictedMask[i, j] == 0:
                        '''Image corresponding mask generated | removing mask zero value coordinates'''
                        ImgCorrMask[i,j,0] = 0
                        ImgCorrMask[i,j,1] = 0
                        ImgCorrMask[i,j,2] = 0
                    elif predictedMask[i, j] == 1:
                        imgSmall[i, j, 0:] = (0, 255, 0)
            
            ImgCorrMaskImage = Image.fromarray(ImgCorrMask.astype('uint8'), 'RGB')
            imgSmallImage = Image.fromarray(imgSmall.astype('uint8'), 'RGB')
            WIDTH, HEIGHT = imgSmallImage.size
            imgLarge = imgSmallImage.resize( (int( (WIDTH*2.1)*ratio_mult ), int( (HEIGHT*2.1)*ratio_mult )), Image.Resampling.LANCZOS )
            img = ImageTk.PhotoImage(imgLarge)
            ImagesAnalyzed.append(img) 
            
            r,g,b = ImgCorrMaskImage.split()
            hist_r = r.histogram()
            hist_r[0] = 0
            hist_g = g.histogram()
            hist_g[0] = 0
            hist_b = b.histogram()
            hist_b[0] = 0
            HistList_Analyzed.append(hist_r)
            HistList_Analyzed.append(hist_g)
            HistList_Analyzed.append(hist_b)
        
        AnalyzedImagesCount = len(ImagesAnalyzed)
        ''' NAMES EXTRACTED '''
        for i in range(0, len(OriginalIndex) ):
            AnalyzedImagePaths[i] = image_names[ OriginalIndex[i] ]
            if masktrue:
                truemask.append( masktrue[OriginalIndex[i]] )
            
        Analysis_complete=True
        tkinter.messagebox.showinfo(title="Response", message="Abnormality detected!")
        ConstructBase(tktop=tktop, initAnstate=False, histMetricstate=True, input_case=False, abnormality=True, image_names=AnalyzedImagePaths, 
                      image_list=ImagesAnalyzed, image_list_index=0, currentdirectory_list=None, hist_list=HistList_Analyzed, 
                      image_list_len=AnalyzedImagesCount, masktrue=truemask, maskpred=maskpred)
    
    else:
        tkinter.messagebox.showinfo(title="Response", message="No abnormality detected!")
        Analysis_complete=True
        ConstructBase(tktop=tktop, initAnstate=False, histMetricstate=True, input_case=False, abnormality=False, image_names=image_names,
                      image_list=image_list_org, image_list_index=0, currentdirectory_list=None, hist_list=hist_list_org, image_list_len=image_list_len_org, 
                      masktrue=masktrue, maskpred=None)


def main():
    global top
    
    global Bg
    global ratio_mult
    
    top = tkinter.Tk()
    top.config(bg="white")
    
    top.title("Classification and Localization of Abnormal Human Brain MR Images")
    small_icon = tkinter.PhotoImage(file="FrontEndIconsDefaultImages\icons8-brain-16.png")
    large_icon = tkinter.PhotoImage(file="FrontEndIconsDefaultImages\icons8-brain-32.png")
    top.iconphoto(False, large_icon, small_icon)
    
    factscreen_w = int(1280)
    factscreen_h = int(720)
    width = top.winfo_screenwidth()
    height = top.winfo_screenheight()
    #top.geometry(str(width)+'x'+str(height)+'+0+0')

    imgSmallmain = Image.open( "FrontEndIconsDefaultImages\square-256.png" )
    WIDTH, HEIGHT = imgSmallmain.size
    ratio_mult = factscreen_w / width

    imgLargemain = imgSmallmain.resize( ( int((WIDTH*2.1)*ratio_mult),int((HEIGHT*2.1)*ratio_mult ) ),Image.Resampling.LANCZOS )
    Bg = ImageTk.PhotoImage( imgLargemain )
    BgSmall = ImageTk.PhotoImage( imgSmallmain )
    
    ConstructBase(tktop=top, initAnstate=False, histMetricstate=False, input_case=False, abnormality=False, image_names=None, image_list=None, 
                  image_list_index=0, currentdirectory_list=None, hist_list=None, image_list_len=0, masktrue=None, maskpred=None)
    
    top.mainloop()


if __name__ == "__main__":
    main()