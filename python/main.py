# -*- coding: UTF-8 -*-

# import numpy as np
import cv2
# import matplotlib.pyplot as plt
import errno
import os
import time

from PIL import Image, ExifTags
from PIL.TiffTags import TAGS
# import exifread
# import piexif
import json
import asyncio


# a = np.eye(3)
# print(a)
#
# a = np.eye(3, k=2)
# print(a)
#
# dt = np.dtype('i8')
# print(dt)
#
# t = np.dtype([('age', np.int16)])
# print(t)
#
# dt = np.dtype([('age', np.int8)])
# a = np.array([10, 20, 30], dtype = dt)
# print(a)
# print(a.shape)
# print(a.strides)
#
# print(a['age'])


# dt = np.dtype('f8')
# print(dt)
#
# student = np.dtype([('name', 'S2'), ('age', 'i1'), ('marks', 'f4')])
# print(student)
#
# a = np.array([('abcdefg', 20, 98.5), ('abcdefg', 30, 99.3), ('abcdefg', 40, 100.3)])
# print(a)
# print(a.ndim)

# a = np.arange(24)
# print(a)
# print(a.ndim)
# print(a.itemsize)
# print(a.flags)
#
# b = a.reshape(4, 6)
# print(b)
# print(b.ndim)
# print(b.itemsize)
#
# c = a.reshape(4, 3, 2)
# print(c)
# print(c.ndim)
# print(c.itemsize)
# print(c.flags)

# '''NumPy 创建数组'''
# x = np.zeros([2, 3], dtype = float, order = 'C')
# print(x)
#
# z = np.ones((2, 2), dtype = [('x','i4'), ('y','f4'), ('z', 'f2')])
# print(z)

# '''NumPy 从已有的数组创建数组'''

# x =  [(1,2,3),(4,5)]
# a = np.asarray(x)
# print (a)
# print(a.ndim)
#
#
# s =  b'Hello World'
# a = np.frombuffer(s, dtype =  'S1', count=2, offset=3)
# print (a)
#
# list = (1, 2, 3, 4, 5)
# it = iter(list)
# print(it)
# x = np.fromiter(it, dtype=int)
# print(x)

# '''NumPy 从数值范围创建数组'''
# x = np.arange(0, 10, 3)
# print(x)
#
# a = np.logspace(0, 2, num=2, base=10)
# print(a)
#
# a = np.logspace(0, 9, 10, base=2)
# print(a)
#
# a = np.array([[1,2,3],[3,4,5],[4,5,6]])
# # print(a)
# print(a[1, ...])
# print(a[..., 1:])
#
# x = np.array([[1,  2],  [3,  4],  [5,  6]])
# print(x)
#
# y = x[[0,1,2],  [0,1,0]]
# '''x(0,0), x(1,1), x(2,0)'''
# print(y)

# '''OpenCV'''

# src = cv2.imread("/Users/cosmos/Desktop/1981563173896_.pic.jpg")
# print(src.shape)
# cv2.imshow("显示灰度图", src)
# cv2.waitKey(0)

# img = Image.open('/Users/cosmos/Desktop/1981563173896_.pic.jpg')
# if hasattr(img, '_getexif'):
#     # 获取exif信息
#     dict_exif = img._getexif()
#     print(dict_exif(274, 0))
#     if dict_exif(274, 0) == 3:
#         # 旋转
#         new_img = img.rotate(-90)
#     elif dict_exif(274, 0) == 6:
#         # 旋转
#         new_img = img.rotate(180)
#     else:
#         new_img = img
# else:
#     new_img = img

# tags = exifread.process_file(open('/Users/cosmos/Desktop/1981563173896_.pic.jpg', 'rb'))
# print(tags)
#
# with Image.open('/Users/cosmos/Desktop/15634321336830.8535762564903417.jpg') as img:
#     meta_dict = {TAGS[key]: img.tag[key] for key in img.tag.iterkeys()}
#     print(meta_dict)
# meta_dict = {
#     TAGS[key] : img.tag[key] for key in img.tag.iterkeys()
# }

def get_exif(fn):
    ret = {}
    i = Image.open(fn)
    #    info = i._getexif()
    info = i.tag.tags
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        ret[decoded] = value
    return ret


def addExif2JpegFile(fullFilename):
    image = Image.open(fullFilename)
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break

    if image._getexif() is not None:
        exif = dict(image._getexif().items())
        print(exif[orientation])
        # if exif[orientation] == 3:
        #     image = image.rotate(180, expand=True)
        # image.save(fullFilename)

    else:
        print("image._getexif() == null")
        exif_dict = {"0th": {},
                     "Exif": {},
                     "GPS": {},
                     "Interop": {},
                     "1st": {},
                     "thumbnail": None}
        exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
        exif_bytes = piexif.dump(exif_dict)
        image.save(fullFilename, "jpeg", exif=exif_bytes)


def renameFileWithTimestamp(path, oldname, timestamp=0):
    # print("current time = " + str(timestamp))
    # print("old file = " + path + "/" + oldname)

    newname = path + "/" + str(timestamp) + "_" + oldname
    oldname = path + "/" + oldname
    print("new file = " + newname)
    os.rename(oldname, newname)


def parseAndSpiltJsonFile(filepath, rootDir):
    f = open(filepath, 'r')
    for line in f.readlines():
        jsonstr = line.split("	")[1]
        jsonobj = json.loads(jsonstr)
        # print(str(jsonobj["time"]) + ":" + jsonobj["facePosition"])

        newJsonData = {}
        newJsonData["personId"] = jsonobj["personId"]
        newJsonData["time"] = jsonobj["time"]
        newJsonData["facePosition"] = jsonobj["facePosition"]
        json_data = json.dumps(newJsonData)
        # print(json_data)

        filename = rootDir + jsonobj["CID"] + ".json"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        cid_file = open(filename, "a")
        cid_file.write(json_data + "\n")
        cid_file.close()


def createTestData(path):
    files = os.listdir(path)

    for file in files:
        if "DS_Store" not in file and "base" not in file:
            personIdMap = {}
            filepath = path + file
            print(filepath)
            f = open(filepath, 'r')
            for line in f.readlines():
                print(line)
                jsonobj = json.loads(line)

                personId = jsonobj["personId"]
                faceList = personIdMap.get(personId)
                if not faceList:
                    faceList = {}
                    faceList[jsonobj["time"]] = jsonobj["facePosition"]
                    personIdMap[personId] = faceList
                else:
                    faceList[jsonobj["time"]] = jsonobj["facePosition"]

            filename = path + "base/" + file.split(".")[0] + "_base.json"
            if not os.path.exists(os.path.dirname(filename)):
                try:
                    os.makedirs(os.path.dirname(filename))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            cid_file = open(filename, "a")
            for k, v in personIdMap.items():
                person = {}
                person["personId"] = k
                person["rectCount"] = len(v)
                person["rects"] = v
                strPerson = json.dumps(person)
                cid_file.write(strPerson + "\n")
            cid_file.close()


def mapBaseDataToImage(baseDataDir, imageDir):
    baseDataFiles = os.listdir(baseDataDir)
    for file in baseDataFiles:
        # print(file)
        if ".DS" in file or "image" in file:
            continue

        cid = file.split("_")[0]
        imageFiles = os.listdir(imageDir + cid)

        f = open(baseDataDir + file, 'r')
        for line in f.readlines():
            # print(line)
            personRecord = json.loads(line)
            faceRectsDict = personRecord["rects"]
            personId = personRecord["personId"].split("-")[4]
            for key, value in faceRectsDict.items():
                point_top_left_x = int(value[0][0] * 1920)
                point_top_left_y = int(value[0][1] * 1080)
                point_bottom_right_x = int(value[2][0] * 1920)
                point_bottom_right_y = int(value[2][1] * 1080)

                for imageFile in imageFiles:
                    # if imageFile.split("_")[0] == key and key == "1564055973377":
                    if imageFile.split("_")[0] == key:
                        dstFile = baseDataDir + "image/" + cid + "/" + key + ".jpg"
                        if not os.path.exists(os.path.dirname(dstFile)):
                            try:
                                os.makedirs(os.path.dirname(dstFile))
                            except OSError as exc:  # Guard against race condition
                                if exc.errno != errno.EEXIST:
                                    raise

                        if os.path.isfile(dstFile):
                            image = cv2.imread(dstFile)
                            imageWithRect = cv2.rectangle(image, (point_top_left_x, point_top_left_y),
                                                          (point_bottom_right_x, point_bottom_right_y), (0, 0, 255), 2)

                            font = cv2.FONT_HERSHEY_SIMPLEX
                            fontScale = 1
                            fontColor = (255, 0, 255)
                            lineType = 2

                            cv2.putText(image, personId,
                                        (point_top_left_x, point_top_left_y+50),
                                        font,
                                        fontScale,
                                        fontColor,
                                        lineType)

                            cv2.imwrite(dstFile, imageWithRect)
                        else:
                            image = cv2.imread(imageDir + cid + "/" + imageFile)
                            imageWithRect = cv2.rectangle(image, (point_top_left_x, point_top_left_y),
                                                          (point_bottom_right_x, point_bottom_right_y), (0, 0, 255), 2)

                            font = cv2.FONT_HERSHEY_SIMPLEX
                            fontScale = 1
                            fontColor = (255, 0, 255)
                            lineType = 2

                            cv2.putText(image, personId,
                                        (point_top_left_x, point_top_left_y+50),
                                        font,
                                        fontScale,
                                        fontColor,
                                        lineType)
                            cv2.imwrite(dstFile, imageWithRect)
        f.close()


def mapTestDataToImage(testDataResultFile, imageDir):
    f = open(testDataResultFile, 'r')
    for line in f.readlines():
        # print(line)
        personRecord = json.loads(line)
        faceRect = personRecord["rect"]
        faceTime = personRecord["time"]
        point_top_left_x = int(faceRect[0])
        point_top_left_y = int(faceRect[2])
        point_bottom_right_x = int(faceRect[1])
        point_bottom_right_y = int(faceRect[3])
        #
        imageFiles = os.listdir(imageDir)

        cid = "5bcd5df905a691d9b0966564"

        # print(faceTime)
        #
        for imageFile in imageFiles:
            # print(str(faceTime) + "--" + imageFile)
            if imageFile.split(".")[0] == str(faceTime):
                print(imageDir + imageFile)
                image = cv2.imread(imageDir + imageFile)
                # print(str(point_top_left_x) + "----"  + str(point_top_left_y))
                # print(str(point_bottom_right_x) + "----"  + str(point_bottom_right_y))
                imageWithRect = cv2.rectangle(image, (point_top_left_x, point_top_left_y),
                                              (point_bottom_right_x, point_bottom_right_y), (255, 0, 0), 2)
                cv2.imwrite(imageDir + imageFile, imageWithRect)

    f.close()


def mat_inter(box1, box2):
    # 判断两个矩形是否相交
    # box=(xA,yA,xB,yB)
    x01, y01, x02, y02 = box1
    x11, y11, x12, y12 = box2

    lx = abs((x01 + x02) / 2 - (x11 + x12) / 2)
    ly = abs((y01 + y02) / 2 - (y11 + y12) / 2)
    sax = abs(x01 - x02)
    sbx = abs(x11 - x12)
    say = abs(y01 - y02)
    sby = abs(y11 - y12)
    if lx <= (sax + sbx) / 2 and ly <= (say + sby) / 2:
        return True
    else:
        return False


def solve_coincide(box1, box2):
    # box=(xA,yA,xB,yB)
    # 计算两个矩形框的重合度
    if mat_inter(box1, box2) == True:
        x01, y01, x02, y02 = box1
        x11, y11, x12, y12 = box2
        col = min(x02, x12) - max(x01, x11)
        row = min(y02, y12) - max(y01, y11)
        intersection = col * row
        area1 = (x02 - x01) * (y02 - y01)
        area2 = (x12 - x11) * (y12 - y11)
        coincide = intersection / (area1 + area2 - intersection)
        return coincide
    else:
        return False


def runTestData(testDataResultFile, baseDataFile):
    fileBase = open(baseDataFile)

    hitCount  = 0
    missCount = 0
    for lineInBase in fileBase.readlines():
        baseFace = json.loads(lineInBase)
        faceRectsDict = baseFace["rects"]
        # hitCount += 1
        hit = False
        for key, value in faceRectsDict.items():
            # print(value)
            base_point_top_left_x = int(value[0][0] * 1920)
            base_point_top_left_y = int(value[0][1] * 1080)
            base_point_bottom_right_x = int(value[2][0] * 1920)
            base_point_bottom_right_y = int(value[2][1] * 1080)

            base_rect = (base_point_top_left_x,
                         base_point_top_left_y,
                         base_point_bottom_right_x,
                         base_point_bottom_right_y)
            #
            fileTest = open(testDataResultFile, 'r')
            for lineInTest in fileTest.readlines():
                testFace = json.loads(lineInTest)
                testTime = testFace["time"]
                if str(testTime) == key:
                    testRect = testFace["rect"]
                    test_point_top_left_x = int(testRect[0])
                    test_point_top_left_y = int(testRect[2])
                    test_point_bottom_right_x = int(testRect[1])
                    test_point_bottom_right_y = int(testRect[3])

                    ret = solve_coincide(
                        base_rect,
                        (test_point_top_left_x, test_point_top_left_y, test_point_bottom_right_x, test_point_bottom_right_y)
                     )

                    if ret and ret > 0.2:
                        # print(str(testTime) + "---" + str(ret))
                        hit = True
                        break
        if not hit and baseFace["rectCount"] != 1:
            print(lineInBase)
            missCount += 1
        else:
            hitCount += 1

    fileBase.close()
    print("Hit Count = " + str(hitCount) + ", miss count = " + str(missCount))

def drawRectOnImage(src_image_path, dst_image_path, left_top_point, right_bottom_point):
    image = cv2.imread(src_image_path)
    imageWithRect = cv2.rectangle(image,
                                  left_top_point,
                                  right_bottom_point,
                                  (255, 0, 0), 2)

    # font = cv2.FONT_HERSHEY_SIMPLEX
    # bottomLeftCornerOfText = (10, 500)
    # fontScale = 1
    # fontColor = (255, 0, 255)
    # lineType = 2
    #
    # cv2.putText(image, 'Hello World!',
    #             left_top_point,
    #             font,
    #             fontScale,
    #             fontColor,
    #             lineType)

    cv2.imwrite(dst_image_path, imageWithRect)

async def hello():
    print("Hello world!")
    r = await asyncio.sleep(1)
    print("Hello again!")

if __name__ == "__main__":
    rootDir = "/Users/cosmos/Desktop/chameleon/"

    
    asyncio.run(hello())


    # parseAndSpiltJsonFile("/Users/cosmos/Desktop/5d4a3dcce0d2254808def966/15651465730190.9265406450435381_list.json", rootDir)

    # createTestData(rootDir)

    # mapBaseDataToImage(rootDir + "base/", "/Users/cosmos/Desktop/")
    # mapTestDataToImage("/Users/cosmos/Desktop/5bcd5df905a691d9b0966564.txt", rootDir + "base/image/")

    # runTestData(
    #     "/Users/cosmos/Documents/tuputech/Chameleon/benchmark/5bcdafef05a691d9b096657a/5bcdafef05a691d9b096657a_recognize.txt",
    #     "/Users/cosmos/Documents/tuputech/Chameleon/chameleon/base/5bcdafef05a691d9b096657a_base.json"
    # )

    # runTestData(
    #     "/Users/cosmos/Documents/tuputech/Chameleon/benchmark/5bce952505a691d9b096657e/5bce952505a691d9b096657e_recognize.txt",
    #     "/Users/cosmos/Documents/tuputech/Chameleon/chameleon/base/5bce952505a691d9b096657e_base.json"
    # )

    # runTestData(
    #     "/Users/cosmos/Documents/tuputech/Chameleon/benchmark/5bcd5df905a691d9b0966564/5bcd5df905a691d9b0966564_recognize.txt",
    #     "/Users/cosmos/Documents/tuputech/Chameleon/chameleon/base/5bcd5df905a691d9b0966564_base.json"
    # )

    # drawRectOnImage("/Users/cosmos/Desktop/5bce952505a691d9b096657e/1564056921900_0010888.jpeg",
    #                 "/Users/cosmos/Desktop/1564056921900_0010888.jpeg",
    #                 (555, 871), (631, 948))
    #
    # drawRectOnImage("/Users/cosmos/Documents/tuputech/Chameleon/5bcd5df905a691d9b0966564/1564056101977_0006843.jpeg",
    #                 "/Users/cosmos/Desktop/1564056101977_0006843.jpeg",
    #                 (402, 486), (607, 692))
    #

    # drawRectOnImage("/Users/cosmos/Desktop/5bcd5df905a691d9b0966564/1564055305177_0002859.jpeg",
    #                 "/Users/cosmos/Desktop/1564055305177_0002859.jpeg",
    #                 (899, 533), (1124, 758))
    #
    # drawRectOnImage("/Users/cosmos/Desktop/test.jpg",
    #                 "/Users/cosmos/Desktop/test.jpg",
    #                 (475, 165), (607, 297))
    # drawRectOnImage("/Users/cosmos/Desktop/test.jpg",
    #                 "/Users/cosmos/Desktop/test.jpg",
    #                 (171, 211), (307, 346))
    # drawRectOnImage("/Users/cosmos/Desktop/test.jpg",
    #                 "/Users/cosmos/Desktop/test.jpg",
    #                 (268, 71), (394, 197))
    # drawRectOnImage("/Users/cosmos/Desktop/test.jpg",
    #                 "/Users/cosmos/Desktop/test.jpg",
    #                 (557, 51), (679, 173))
    # drawRectOnImage("/Users/cosmos/Desktop/test.jpg",
    #                 "/Users/cosmos/Desktop/test.jpg",
    #                 (354, 207), (482, 336))
    # drawRectOnImage("/Users/cosmos/Desktop/test.jpg",
    #                 "/Users/cosmos/Desktop/test.jpg",
    #                 (377, 29), (503, 155))
    # drawRectOnImage("/Users/cosmos/Desktop/test.jpg",
    #                 "/Users/cosmos/Desktop/test.jpg",
    #                 (612, 214), (739, 341))
    # drawRectOnImage("/Users/cosmos/Desktop/test.jpg",
    #                 "/Users/cosmos/Desktop/test.jpg",
    #                 (700, 112), (810, 221))

    # ret = solve_coincide((415, 629, 615, 829), (272, 595, 475, 798))
    # print(ret)

    # path = "/Users/cosmos/Desktop/5b7a7f2c1ef956748a0fbb50"
    # files = os.listdir(path)
    # files.sort(key=lambda x: int(x[:-5]))
    #
    # t = time.time()
    # timestamp = int(round(t * 1000))
    #
    # for file in files:
    #     fullFilename = path + "/" + file
    #     # print(file)
    #     # fullFilename = file
    #
    #     # image = Image.open(fullFilename)
    #     # data = list(image.getdata())
    #     # image_without_exif = Image.new(image.mode, image.size)
    #     # image_without_exif.putdata(data)
    #     #
    #     # image_without_exif.save(fullFilename)
    #
    #     # addExif2JpegFile(fullFilename)
    #     timestamp = timestamp + 200
    #     renameFileWithTimestamp(path, file, timestamp)

    # im = Image.open(fullFilename)
    # exif_dict = piexif.load(im.info["Exif"])
    # if exif_dict is None:
    #     print(exif_dict)
    #     piexif.remove(fullFilename)
    # else:
    #     exif_dict = {"0th": {},
    #                  "Exif": {},
    #                  "GPS": {},
    #                  "Interop": {},
    #                  "1st": {},
    #                  "thumbnail": None}
    #     exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
    #     exif_bytes = piexif.dump(exif_dict)
    #     im.save(fullFilename, "jpeg", exif=exif_bytes)

# # exif_dict = piexif.load(im.info["exif"])
# exif_dict = {"0th": {},
#              "Exif": {},
#              "GPS": {},
#              "Interop": {},
#              "1st": {},
#              "thumbnail": None}
# # process im and exif_dict...
# w, h = im.size
# exif_dict["0th"][piexif.ImageIFD.Orientation] = 3
# exif_bytes = piexif.dump(exif_dict)
# im.save(newFilename, "jpeg", exif=exif_bytes)
#
# try:
#     image = Image.open(filepath)
#     for orientation in ExifTags.TAGS.keys():
#         if ExifTags.TAGS[orientation] == 'Orientation':
#             break
#     # exif = dict(image._getexif().items())
#     # print(image._getexif().items())
#     # if exif[orientation] == 3:
#     #     image = image.rotate(180, expand=True)
#     # elif exif[orientation] == 6:
#     #     image = image.rotate(270, expand=True)
#     # elif exif[orientation] == 8:
#     #     image = image.rotate(90, expand=True)
#     image.save(filepath)
#     image.close()
#
# except (AttributeError, KeyError, IndexError):
#     # cases: image don't have getexif
#     pass

'''OpenCV end'''

'''NumPy 高级索引'''
# x = np.array([[  0,  1,  2],[  3,  4,  5],[  6,  7,  8],[  9,  10,  11]])
# print ('我们的数组是：' )
# print (x)
# print ('\n')
# rows = np.array([[0,0],[3,3]])
# cols = np.array([[0,2],[0,2]])
# # print(rows)
# y = x[rows,...]
# # print  ('这个数组的四个角元素是：')
# print (y)

# a = np.array([[1,2,3], [4,5,6],[7,8,9]])
# print(a)
#
# print('\n')
#
# b = a[1:3, 2:3]
# c = a[1:3,[1,2]]
# d = a[...,1:]
# # print(b)
# # print(c)
# # print(d)
# print(a[[1,2]])
# print(a[a > 2])
#
# '''x:代表只负责从第几行到第几行, y:代表第几列到第几列'''
# '''--------------'''
#
# '''花式索引'''
# x = np.arange(32).reshape((8,4))
# print(x)
# # print(x[[4,2,1,7]])
# # print(x[[-4,-2,-1,-7]])
# print (x[np.ix_([1,5,7,2],[0,3,1,2])])
# '''
#     x(1,0) x(1,3) x(1,1) x(1,2)
#     x(5,0) x(5,3) x(5,1) x(5,2)
#     x(7,0) x(7,3) x(7,1) x(7,2)
#     x(2,0) x(2,3) x(2,1) x(2,2)
# '''
#
# x = np.float32(np.random.rand(2, 3))
# print(x)
