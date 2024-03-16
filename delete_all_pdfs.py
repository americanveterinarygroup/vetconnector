import os 

r = []
dir = './pdfs/'                                                                                                          
subdirs = [x[0] for x in os.walk(dir)]                                                                            
for subdir in subdirs:                                                                                         
    files = os.walk(subdir).__next__()[2]                                                                             
    if (len(files) > 0):                                                                                          
        for file in files:         
            f = os.path.join(subdir, file)                                                                               
            os.remove(f)
            print(f"file deleted: {f}")