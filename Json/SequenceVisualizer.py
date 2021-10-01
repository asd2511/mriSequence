from os import times
import matplotlib.pyplot as plt
import numpy as np
import json
import cv2
from matplotlib.colors import hsv_to_rgb as hsv2rgb
from glob import glob
import matplotlib.ticker as plticker
from tqdm import tqdm
import os

def _flow2rgb(flow):
    # cart to polar
    ang = (np.arctan2(flow[0], flow[1]) * 180 /3.1415926 + 180) / 360
    mag = np.sqrt(flow[0]**2+flow[1]**2)/np.sqrt(2)
    if type(flow[0]) != type(np.float64(0.0)):
        hsv = np.zeros([flow[0].shape[0],flow[0].shape[1],3])
        # # flow(polar) to hsv
        hsv[...,0] = ang * 255
        hsv[...,1] = min(mag.any() * 255,255)
        hsv[...,2] = 255
    else:
        hsv = np.zeros([3])
        # # flow(polar) to hsv
        hsv[0] = ang * 255
        hsv[1] = min(mag * 255,255)
        hsv[2] = 255
    # hsv to rgb
    return hsv2rgb(hsv/255.0)

def showWheel():
    plt.figure("hsv wheel",figsize=(3,3))
    for i in range(360):
        x = np.sin(i*np.pi/180)
        y = np.cos(i*np.pi/180)
        plt.plot([0,x],[0,y],color=_flow2rgb([x,y]))


def loadJson(path="sequence.json"):
    with open(path,"r") as f:
        data = json.load(f)
    return data

def cart2polar(data, scaleVector=20, scaleTime=1000):
    totalTime = 0
    polarData = []
    for r in range(data["param"]["#Rep"])[:3]:
        for t in range(data["param"]["#Event"]):
    # for r in range(data["param"]["#Event"]):
    #     for t in range(data["param"]["#Rep"]):
            x = np.array(data["spin"]["x"][str(r)][str(t)]) * scaleVector
            y = np.array(data["spin"]["y"][str(r)][str(t)]) * scaleVector
            z = np.array(data["spin"]["z"][str(r)][str(t)])

            time = np.array(data["spin"]["t"][str(r)][str(t)]) * scaleTime

            angle,phase,_,_ = np.array(data["sequence"]["flip"][str(r)][str(t)])
            angle = angle*180/np.pi
            phase = phase*180/np.pi
            gx = np.array(data["sequence"]["gradient"][str(r)][str(t)])[:,1]
            gy = np.array(data["sequence"]["gradient"][str(r)][str(t)])[:,0]

            totalTime += np.round(time,2)

            mag, ang = cv2.cartToPolar(x,y)
            polarData.append([[mag, ang, z], np.round(totalTime,2),[angle,phase,gx,gy,r,t]] )

    return polarData

def interpolationInTime(polarData,timeStep = 0.01):
    [[mag, ang, z], _,_] = polarData[-1]
    magPrev = np.zeros_like(mag)
    angPrev = np.zeros_like(ang)
    zPrev = np.zeros_like(z)

    timeNow = 0
    allTimeData = []
    for [mag, ang, zDirec], total, param in polarData:
        mDiff = (mag-magPrev)
        aDiff = (ang-angPrev)
        zDiff = (zDirec-zPrev)

        # aDiff[aDiff<0] += 2*np.pi
        # aDiff[aDiff>0] -= 2*np.pi
        timeDiff = total-timeNow
        tStep = max( timeStep, timeDiff/10.0)
        while timeNow <= total:
            v = 1-((total-timeNow) / timeDiff)
            timeNow += tStep
            zNew = zPrev + zDiff*v
            x,y = cv2.polarToCart(magPrev+mDiff*v,angPrev+aDiff*v)
            allTimeData.append([[x, y, zNew], np.round(timeNow,2), param])
        magPrev = mag
        angPrev = ang
        zPrev = zDirec
    return allTimeData

def plotImage(dataJson, dataSeq, scaleTime, timeStep, scale, title, isHSVWheel=True):
    # if isHSVWheel: showWheel()

    fig = plt.figure(title,figsize=(16,8))
    axs = fig.subplots(1,2)
    ax = axs[0]
    ax1 = axs[1]

    xCood = np.arange(dataJson["param"]["size"][0])
    yCood = np.arange(dataJson["param"]["size"][0])
    xv,yv = np.meshgrid(xCood,yCood,indexing="xy")
    xv = xv.flatten()
    yv = yv.flatten()
    for [x, y, z], currentTime, [angle,phase,gx,gy,r,t] in tqdm(dataSeq):
        time = np.round(dataJson["spin"]["t"][str(r)][str(t)] * scaleTime,2)
        fig.suptitle("NRep: {}, NEvent: {}".format(r,t))
        ax.set_title("EventTime: {} ms, currentTime: {} ms".format(time,np.round(currentTime,2)))
        ax1.set_title("rf angle: {}, rf phase: {}".format(np.round(angle,2), np.round(phase,2) ))

        if isHSVWheel:
            colorWheel = _flow2rgb([x,y])
            for i in range(dataJson["param"]["size"][0]):
                for j in range(dataJson["param"]["size"][1]):
                    ax.plot([i*scale,i*scale+x[i,j]],[j*scale,j*scale+y[i,j]],color=colorWheel[i,j],linewidth=3.5)
                    ax1.plot([i*scale,i*scale],[j*scale,j*scale+z[i,j]],color=(1,0,0),linewidth=3.5)
        else:
            x = x.flatten()
            y = y.flatten()
            z = z.flatten()
            coodBase = np.array([xv,yv]).T
            coodZ = np.array([xv,yv+z]).T*scale
            coodXY = np.array([xv+x,yv+y]).T*scale
            ax.plot([coodBase[:,0]*scale,coodXY[:,0]],[coodBase[:,1]*scale,coodXY[:,1]],color=(1,0,0),linewidth=3.5)
            ax1.plot([coodBase[:,0]*scale,coodZ[:,0]],[coodBase[:,1]*scale, coodZ[:,1]],color=(1,0,0),linewidth=3.5)

        loc = plticker.MultipleLocator(base=scale)

        ax.xaxis.set_major_locator(loc)
        ax.yaxis.set_major_locator(loc)
        ax.grid(linestyle="dotted")
        ax.set_yticks(np.arange(len(gy)))
        ax.set_xticks(np.arange(len(gx)))
        ax.set_yticklabels(gy,fontsize=7)
        ax.set_xticklabels(gx,fontsize=7)
        ax.set_xlabel('Gx (frequency)')
        ax.set_ylabel('Gy (phase)')

        ax1.xaxis.set_major_locator(loc)
        ax1.yaxis.set_major_locator(loc)
        ax1.grid(linestyle="dotted")
        ax.set_yticklabels(gy,fontsize=7)
        ax.set_xticklabels(gx,fontsize=7)
        ax1.set_xlabel('voxel x')
        ax1.set_ylabel('voxel y')
        plt.pause(timeStep)
        # fig.savefig("fig_{}.png".format(currentTime),dpi=150)
        ax.clear()
        ax1.clear()

def showImage(dataJson, dataSeq, scaleTime, timeStep, scale, title, isHSVWheel=True):
    # if isHSVWheel: showWheel()

    fig = plt.figure(title,figsize=(16,8))
    axs = fig.subplots(1,2)
    ax = axs[0]
    ax1 = axs[1]

    xCood = np.arange(dataJson["param"]["size"][0])
    yCood = np.arange(dataJson["param"]["size"][0])
    xv,yv = np.meshgrid(xCood,yCood,indexing="xy")
    xv = xv.flatten()
    yv = yv.flatten()

    xCood = np.arange(dataJson["param"]["size"][0])
    yCood = np.arange(dataJson["param"]["size"][1])
    xv,yv = np.meshgrid(xCood,yCood,indexing="xy")
    xv = xv.flatten()
    yv = yv.flatten()
    for [x, y, z], currentTime, [angle,phase,gx,gy,r,t] in tqdm(dataSeq):
        time = np.round(dataJson["spin"]["t"][str(r)][str(t)] * scaleTime,2)
        fig.suptitle("NRep: {}, NEvent: {}".format(r,t))
        ax.set_title("EventTime: {} ms, currentTime: {} ms".format(time,np.round(currentTime,2)))
        ax1.set_title("rf angle: {}, rf phase: {}".format(np.round(angle,2), np.round(phase,2) ))
        canvas1 = np.ones([(dataJson["param"]["size"][0]-1)*scale,( dataJson["param"]["size"][1]-1)*scale,3])*0.25
        canvas2 = np.ones([(dataJson["param"]["size"][0]-1)*scale,( dataJson["param"]["size"][1]-1)*scale,3])*0.25

        colorWheel = _flow2rgb([x,y])[:,:,::-1]
        x = x.flatten()
        y = y.flatten()
        z = z.flatten()

        coodBase = np.array([yv,xv]).T
        coodZ = (np.array([yv,xv-z]).T*scale).astype(np.uint)
        coodXY = (np.array([yv+y,xv+x]).T*scale).astype(np.uint)

        for start, endXY,endZ in zip(coodBase,coodXY,coodZ):
            cv2.line(canvas1, start*scale, endXY, colorWheel[start[0],start[1]], 2, cv2.LINE_AA)
            cv2.line(canvas2, start*scale, endZ,  (1,0,0), 2, cv2.LINE_AA)

        ax.imshow( canvas1[:,:,:])
        ax1.imshow(canvas2[:,:,:])

        ax.set_xticks(np.arange(len(gx))*scale)
        ax.set_yticks(np.arange(len(gy))*scale)
        ax.set_xticklabels(np.round(gx,2),fontsize=7)
        ax.set_yticklabels(np.round(gy,2),fontsize=7)
        ax.set_xlabel('Gx (frequency)')
        ax.set_ylabel('Gy (phase)')

        ax1.set_xticks(np.arange(len(gx))*scale)
        ax1.set_yticks(np.arange(len(gy))*scale)
        ax1.set_yticklabels(np.round(gy,2),fontsize=7)
        ax1.set_xticklabels(np.round(gx,2),fontsize=7)
        ax1.set_xlabel('voxel x')
        ax1.set_ylabel('voxel y')
        plt.pause(timeStep*10)
        fig.savefig("figure\\fig_{}.png".format(int(currentTime*100)),dpi=200)
        ax.clear()
        ax1.clear()
        # canvas = np.hstack([canvas1, canvas2])
        # cv2.imshow("Spin space",canvas)
        # cv2.waitKey(100)

def videoMaker(name):
    fps = 1          # 视频帧率
    size = (1600, 800) # 需要转为视频的图片的尺寸
    seqName = name.split("//")[-1].split(".")[0]
    video = cv2.VideoWriter(seqName+".avi", cv2.VideoWriter_fourcc('M', 'P', '4', '2'), fps, size)
    for path in tqdm(sorted(glob('figure\\*.png'), key=os.path.getmtime)):
        img =cv2.resize(cv2.imread(path),size)
        video.write(img)
        os.remove(path)
    video.release()
    cv2.destroyAllWindows()

def main(path, timeInter=True, isHSV=True):
    dataJson = loadJson(path)
    seqName = path.split("//")[-1].split(".")[0]
    seq = cart2polar(data=dataJson, scaleVector=2, scaleTime=1000) # polar Discrete
    if timeInter:
        seq = interpolationInTime(seq, timeStep = 0.01) # cart Continue
    # plotImage(dataJson, seq, 1000, 0.01, 5, "Sequence of "+seqName, isHSVWheel=isHSV)
    showImage(dataJson, seq, 1000, 0.01, 25, "Sequence of "+seqName, isHSVWheel=isHSV)



if __name__ == "__main__":
    filePath = "SequenceJson\\Spinecho.json" 
    main(filePath,timeInter=1,isHSV=1)
    # videoMaker(filePath)

