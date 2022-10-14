#!/usr/bin/python
# -*- coding:utf-8 -*-
import fcntl
import json
import os
import re
import socket
import struct
import subprocess
import sys
import time
import urllib.request






# 新建一个多进程来执行命令的方法
def run(cmd, cwd=None):
    #print('%srun:%s %s' % (COLOR_GREEN, COLOR_DEFAULT, cmd))
    process = subprocess.Popen(cmd.split(), env=os.environ, cwd=cwd,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = []
    while process.returncode is None:
        line = process.stdout.readline()
        if len(line) == 0:
            break
        output.append(line.rstrip().decode('utf-8'))
    process.communicate()
    #assert process.returncode == 0
    return output


# ping 检测的模块
def ping_loss(hostinfo):
    # cameras: [ {"CID-1"："online", "CID-2": "offline", "CID-3": "lostPackage" , ... } ]
    cid = hostinfo.split(':')[0]
    host = hostinfo.split(':')[1]

    pak_nums = 5
    #print('Running: %s' % host)
    infos = run('ping -q -c %d -w %d %s' % ( pak_nums , pak_nums+2 , host ))
    #print('Finished: %s' % host)
    for info in infos:
        if 'packet loss' in info:
            info_split=info.strip().split(',')
            for inf in info_split:
                if 'packet loss' in inf:
                    packet_loss_str = inf
                    packet_loss_num = packet_loss_str.split('%')[0].strip()
                    if int(packet_loss_num) == 0:
                        camera_status = "online"
                    elif int(packet_loss_num) == 100:
                        camera_status = "offline"
                    else:
                        camera_status = "lostPackage"

                    loss_pak = { cid : camera_status }
                    return loss_pak

# 上传摄像头状态
def post_camera_status(lists):
    request = urllib.request.Request(api_url)
    request.add_header('User-Agent', user_agent)
    request.add_header('Content-Type', 'application/json')
    
    data={}
    for i in lists:
        data.update(i)
    print("Camera status json: %s" % data)
    try:
        response = urllib.request.urlopen(request,json.dumps(data), timeout=10)
        #response_json = json.loads(response.read())
        #print response_json
        print('post data successful')
    except:
        print('fail to post data')
    

def getHwAddr(ifname): 
    # 获取盒子自带有线网卡的MAC地址
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15])) 
    return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1] 


def get_hw_address(ifname):
    # 获取盒子自带有线网卡的MAC地址
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    info = fcntl.ioctl(s.fileno(),0x8927,struct.pack('256s', ifname[:15]))
    hwaddr = []
    # print len(info)
    for char in info[18:24]:
        hdigit = '%02x' % struct.unpack('B',char)[0]
        hwaddr.append(hdigit)
    return '-'.join(hwaddr)


def get_camip(rtsp):
    # 通过正则获得摄像头的IP地址
    reg = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    camera_ip = re.findall(reg,rtsp)[0]
    return camera_ip

def create_camera_proxy(key_deviceid, listenPort, listenIP):
    # 写入摄像头反向代理的NGINX配置
    confpath="/etc/nginx/conf.d/"
    democonf= confpath + "nginx_demo.conf.bak"
    cam_conf= confpath + 'cam_' + key_deviceid + '.conf'
    os.system("/usr/bin/cp -f %s %s" % (democonf , cam_conf))
    os.system("sed -i 's@%s@%s@' %s" % ('listenPort' , listenPort , cam_conf))
    os.system("sed -i 's@%s@%s@' %s" % ('listenIP' , listenIP , cam_conf))
    os.system('/sbin/nginx -s reload')


def write_conf(deviceid, ffmpeg_command):
    # 写入 supervisord 配置文件   
    supervisord_dir = '/etc/supervisord.d/'                                                                                                          
    supervisord_conf = supervisord_dir + deviceid + ".conf"                                                  
    conf_files = open(supervisord_conf,'w')                                                                                     
    conf_files.write( "[program:%s]\n" % deviceid )                                                          
    conf_files.write( "command = sh -c 'ulimit -c 256 -v 1048576 && exec %s'\n" % ffmpeg_command )                              
    conf_files.write( "directory= /var/log/ffmpeg/\n" )                                                                         
    conf_files.write( "autostart = true\n" )                                                                                    
    conf_files.write( "startsecs = 5\n" )                                                                                       
    conf_files.write( "autorestart = true\n" )                                                                                  
    conf_files.write( "startretries = 1000000\n" )                                                                              
    conf_files.write( "redirect_stderr = true\n" )                                                                              
    conf_files.write( "stdout_logfile_maxbytes = 10MB\n" )                                                                      
    conf_files.write( "stdout_logfile_backups = 10\n" )                                                                         
    conf_files.write( "stdout_logfile = /var/log/ffmpeg/%s.log\n" % deviceid )
    print("write in supervisord conf : %s" % supervisord_conf)
    conf_files.close()

macList=[
"a8:3f:a1:30:d0:3c",
"a8:3f:a1:30:d0:38",
"a8:3f:a1:30:d0:39",
"a8:3f:a1:30:d0:37",
"a8:3f:a1:30:d0:36",
"a8:3f:a1:30:d0:33",
"a8:3f:a1:30:d0:32",
"a8:3f:a1:30:d0:31",
"a8:3f:a1:30:d0:30",
"a8:3f:a1:30:d0:2f",
"a8:3f:a1:30:d0:2e",
"a8:3f:a1:30:d0:2d",
"a8:3f:a1:30:d0:2c",
"a8:3f:a1:30:d0:28",
"a8:3f:a1:30:d0:27",
"a8:3f:a1:30:d0:26",
"a8:3f:a1:30:d0:25",
"a8:3f:a1:30:d0:24",
"a8:3f:a1:30:d0:3c",
"a8:3f:a1:30:d0:38",
"a8:3f:a1:30:d0:39",
"a8:3f:a1:30:d0:37",
"a8:3f:a1:30:d0:36",
"a8:3f:a1:30:d0:33",
"a8:3f:a1:30:d0:32",
"a8:3f:a1:30:d0:31",
"a8:3f:a1:30:d0:30",
"a8:3f:a1:30:d0:2f",
"a8:3f:a1:30:d0:2e",
"a8:3f:a1:30:d0:2d",
"a8:3f:a1:30:d0:2c",
"a8:3f:a1:30:d0:28",
"a8:3f:a1:30:d0:27",
"a8:3f:a1:30:d0:26",
"a8:3f:a1:30:d0:25",
"a8:3f:a1:30:d0:24",
"a8:3f:a1:30:d0:86",
"a8:3f:a1:30:d0:87",
"a8:3f:a1:30:d0:88",
"a8:3f:a1:30:d0:89",
"a8:3f:a1:30:d0:8a",
"a8:3f:a1:30:d0:8b",
"a8:3f:a1:30:d0:8c",
"a8:3f:a1:30:d0:8d",
"a8:3f:a1:30:d0:8e",
"a8:3f:a1:30:d0:8f",
"a8:3f:a1:30:d0:90",
"a8:3f:a1:30:d0:91",
"a8:3f:a1:30:d0:92",
"a8:3f:a1:30:d0:93",
"a8:3f:a1:30:d0:94",
"a8:3f:a1:30:d0:95",
"a8:3f:a1:30:d0:96",
"a8:3f:a1:30:d0:97",
"a8:3f:a1:30:d0:98",
"a8:3f:a1:30:d0:99",
"a8:3f:a1:30:d0:9a",
"a8:3f:a1:30:d0:9b",
"a8:3f:a1:30:d0:9c",
"a8:3f:a1:30:d0:9d",
"a8:3f:a1:30:d0:9e",
"a8:3f:a1:30:d0:9f",
"a8:3f:a1:30:d0:a0",
"a8:3f:a1:30:d0:a1",
"a8:3f:a1:30:d0:a2",
"a8:3f:a1:30:d0:a3",
"a8:3f:a1:30:d0:a4",
"a8:3f:a1:30:d0:a5",
"a8:3f:a1:30:d0:a6",
"a8:3f:a1:30:d0:a7",
"a8:3f:a1:30:d0:a8",
"a8:3f:a1:30:d0:a9",
"a8:3f:a1:30:d0:aa",
"a8:3f:a1:30:d0:ab",
"a8:3f:a1:30:d0:ac",
"a8:3f:a1:30:d0:ad",
"a8:3f:a1:30:d0:ae",
"a8:3f:a1:30:d0:af",
"a8:3f:a1:30:d0:b0",
"a8:3f:a1:30:d0:b1",
"a8:3f:a1:30:d0:b2",
"a8:3f:a1:30:d0:b3",
"a8:3f:a1:30:d0:b4",
"a8:3f:a1:30:d0:b5",
"a8:3f:a1:30:d0:b6",
"a8:3f:a1:30:d0:b7",
"a8:3f:a1:30:d0:b8",
"a8:3f:a1:30:d0:b9",
"a8:3f:a1:30:d0:ba",
"a8:3f:a1:30:d0:bb",
"a8:3f:a1:30:d0:bc",
"a8:3f:a1:30:d0:bd",
"a8:3f:a1:30:d0:be",
"a8:3f:a1:30:d0:bf",
"a8:3f:a1:30:d0:c0",
"a8:3f:a1:30:d0:c1",
"a8:3f:a1:30:d0:c2",
"a8:3f:a1:30:d0:c3",
"a8:3f:a1:30:d0:c4",
"a8:3f:a1:30:d0:c5",
"a8:3f:a1:30:d0:c6",
"a8:3f:a1:30:d0:c7",
"a8:3f:a1:30:d0:c8",
"a8:3f:a1:30:d0:c9",
"a8:3f:a1:30:d0:ca",
"a8:3f:a1:30:d0:cb",
"a8:3f:a1:30:d0:cc",
"a8:3f:a1:30:d0:cd",
"a8:3f:a1:30:d0:ce",
"a8:3f:a1:30:d0:cf",
"a8:3f:a1:30:d0:d0",
"a8,:3f:a1:30:d0:d",
"a8:3f:a1:30:d0:d2",
"a8:3f:a1:30:d0:d3",
"a8:3f:a1:30:d0:d4",
"a8:3f:a1:30:d0:d5"]

blackMacList=["a8:3f:a1:30:d0:3b", "a8:3f:a1:30:d0:3a", "a8:3f:a1:30:d0:35", "a8:3f:a1:30:d0:34"]
tokenUrl="https://access.tuputech.com/v1/fa/auth/token"
uidUrl="https://access.tuputech.com/v2/fa/settings/get"
baseUrl="https://bi.tuputech.com/access-control/device?UID="
modelUrl="https://access.tuputech.com/v2/fa/settings/model_info"
kibanaUrl="http://kibana.log.tupu.local/app/kibana#/discover?_g=(refreshInterval:(display:Off,pause:!f,value:0),time:(from:now-30d,mode:quick,to:now))&_a=(columns:!(json.log.mac,json.log.versionName),filters:!(('$state':(store:appState),meta:(alias:!n,disabled:!f,index:'146d3840-93fa-11e9-aebc-5562367c196a',key:json.log.mac,negate:!f,params:(query:'2A:6D:B7:1C:68:92',type:phrase),type:phrase,value:'2A:6D:B7:1C:68:92'),query:(match:(json.log.mac:(query:'2A:6D:B7:1C:68:92',type:phrase))))),index:'146d3840-93fa-11e9-aebc-5562367c196a',interval:s,query:(language:lucene,query:''),sort:!(json.log.time,desc))"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

def getVersionWithMac(mac):
    try:
        req = urllib.request.Request(kibanaUrl)
        # response_json = json.loads(req)
        # print(type(response_json))
        with urllib.request.urlopen(req) as f:
            res = f.read()
            print(res)
            # successTTS = json.loads(res)["data"]["deviceConfig"]["ttsConfig"]["successTTS"]
            # # print(baseUrl+UID)
            # print(successTTS)
            # parseTokenFromResStr(mac, token)
            # return json.loads(res)["data"]["token"]
        #     parseTokenFromResStr(res.decode())
    except Exception as e:
        print(e)

def getModelHash(mac, token):
    try:
        req = urllib.request.Request(modelUrl+"?mac=" + mac)
        req.add_header('token', token)
        # response_json = json.loads(req)
        # print(type(response_json))
        with urllib.request.urlopen(req) as f:
            res = f.read()
            fileHash = json.loads(res)["data"]["frame"]["fileHash"]
            return fileHash
            # successTTS = json.loads(res)["data"]["deviceConfig"]["ttsConfig"]["successTTS"]
            # # print(baseUrl+UID)
            # print(successTTS)
            # parseTokenFromResStr(mac, token)
            # return json.loads(res)["data"]["token"]
        #     parseTokenFromResStr(res.decode())
    except Exception as e:
        print(e)

def parseTokenFromResStr(mac, token):
    try:
        req = urllib.request.Request(uidUrl+"?mac=" + mac)
        req.add_header('token', token)
        # response_json = json.loads(req)
        # print(type(response_json))
        with urllib.request.urlopen(req) as f:
            res = f.read()
            # print(res.decode('utf-8'))
            UID = json.loads(res)["data"]["UID"]
            successTTS = json.loads(res)["data"]["deviceConfig"]["ttsConfig"]["successTTS"]
            # print(baseUrl+UID)
            # print(successTTS)
            return {"UID": UID, "successTTS": successTTS}
            # parseTokenFromResStr(mac, token)
            # return json.loads(res)["data"]["token"]
        #     parseTokenFromResStr(res.decode())
    except Exception as e:
        print(e)

def getUidWithMac(mac):
    try:
        payload = {'mac': mac}
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(tokenUrl, data, headers)
        # response_json = json.loads(req)
        # print(type(response_json))
        with urllib.request.urlopen(req) as f:
            res = f.read()
            # print(res)
            token = json.loads(res)["data"]["token"]
            # print(token)
            resultBag = parseTokenFromResStr(mac, token)
            modelHash = getModelHash(mac, token)

            print(baseUrl+resultBag["UID"] + "   " + resultBag["successTTS"] + "   " + modelHash)
            # return json.loads(res)["data"]["token"]
        #     parseTokenFromResStr(res.decode())
    except Exception as e:
        print(e)

# getVersionWithMac("hh")
# for mac in macList:
# # for mac in blackMacList:
#     getUidWithMac(mac)

    # jsonRes = json.load(res)
    # print(res)

# getUidWithMac("a8:3f:a1:30:d0:24")
# print(getUidWithMac(macList[0]))
# print(getTokenWithMac(macList[0]))
# pprint(data)
#

#
# def getUidWithMac(mac):
#     try:
#         request = urllib.request.Request(url)
#
#         headers = {
#             "Content-Type": "application/json",
#             "Accept": "application/json",
#         }
#         request.add_header('Content-Type', 'application/json; charset=utf-8')
#
#         payload = {'mac': mac}
#
#         response = urllib.request.urlopen(request, json.dumps(payload))
#         # print("Request from %s finish ~" % api_url)
#         response_json = json.loads(response.read())
#         # data_json = json.loads(response_json['data'])
#         print("Request from %s finish ~" % response)
#         # sys.exit()
#     except:
#         print("Get %s error,exit now ~" % api_url)
#         sys.exit()
#
# getUidWithMac(macList[0])
# sys.exit()

# 打印出开始时间
print("\n>>>>>>> %s <<<<<<" % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
# net_device=os.popen("/sbin/ip address | grep '^2:' | cut -d':' -f 2").read().strip()
# box_mac=get_hw_address(net_device)
# print("box_mac: %s" % box_mac)
box_mac="a8:3f:a1:30:01:ba"
box_mac="a8:3f:a1:30:05:58"
box_mac="a8:3f:a1:30:0a:0c"
box_mac="a8:3f:a1:30:00:e0"
# box_mac="a8:3f:a1:30:00:e0"
# box_mac="a8:3f:a1:30:09:ef"
# box_mac="a8-3f-a1-30-09-e1"

api_url = 'https://api.bi.tuputech.com/v1/inner/camera/config/json'
user_agent = 'tupu-smart-endpoint:1.0/cap_a8:3f:a1:30:0a:10'
# user_agent = 'user-agent:tupu-smart-endpoint:1.0/box_a8:3f:a1:30:05:ee'
json_key = 'configuration'

try:
    request = urllib.request.Request(api_url)
    request.add_header('User-Agent', user_agent)
    response = urllib.request.urlopen(request, timeout=10)
    # print("Request from %s finish ~" % api_url)
    response_json = json.loads(response.read())
    data_json = json.loads(response_json['data'])
    print("Request from %s finish ~" % data_json)
    # print("Request from %s finish ~" % response_json)

    # sys.exit()
except:
    print("Get %s error,exit now ~" % api_url)
    sys.exit()


# data_json 是盒子的所有配置信息
# for key in data_json:
#     print(data_json)
    # data_json[json_key] 包含的是所有摄像头的配置信息，是一个长列表
    # if key == json_key:
    #     if len(data_json[key]) == 0 :
    #         # 如果BI上已经关闭所有的摄像头了，盒子也删掉所有推流配置
    #         print('No camera is online,stop push all stream now ~')
    #         os.system("rm -f /etc/supervisord.d/box_*")
    #         os.system("rm -f /home/md5_box*")
    #         break
    #
    #     # 格式化输出所有包含所有摄像头配置的 json 信息
    #     print(json.dumps(data_json[key] , indent=4))
    #     # new add
    #     camera_ip_list = []
    #     for cam in data_json[key]:
    #         rtsp = cam['rtsp']
    #         camera_ip = get_camip(rtsp)
    #         camera_ip_list.append( "%s:%s" % ( cam['CID'], camera_ip ))
    #         # print "CID: %s , camera_ip: %s" % (cam['CID'],camera_ip)
    #
    #     # 批量 ping 所有摄像头然后上传摄像头状态
    #     pool = Pool(processes=30)
    #     status_lists = pool.map(ping_loss, camera_ip_list)
    #     post_camera_status(status_lists)
    #
    #
    #     # 将当前json写入临时文件 /home/md5_box_tmp.json
    #     config_json = '/home/md5_box.json'
    #     config_json_tmp = '/home/md5_box_tmp.json'
    #     jsons = open(config_json_tmp,'w')
    #     jsons.write(json.dumps(data_json[key] , indent=4))
    #     jsons.close()
    #
    #     # 删除不需要的json行，生成一个新的json
    #     for strs in ["enable","name","CID","state","ffmpeg"]:
    #         os.system("sed -i '/%s.:/d' %s" % (strs,config_json_tmp))
    #
    #     if os.path.exists(config_json):
    #         # 如果 /home/md5_box.json 存在，则说明曾经从BI上拉取过配置
    #         print("%s is exits , compare md5 now ~ " % config_json)
    #         # 计算以前json的md5
    #         md5file = open(config_json,'rb')
    #         md5_old = hashlib.md5(md5file.read()).hexdigest()
    #         md5file.close()
    #         #print "/home/md5_box.json: %s" % md5_old
    #         # 计算刚刚得到的json的md5
    #         md5file = open(config_json_tmp,'rb')
    #         md5_now = hashlib.md5(md5file.read()).hexdigest()
    #         md5file.close()
    #         #print "/home/md5_box_tmp.json: %s" % md5_now
    #         if md5_old == md5_now :
    #             print("Camera config json has nothing change , exit now ~")
    #             break
    #         else :
    #             # 如果两个json不一致，以最新的为准
    #             print("Camera config json have changed , update now ~")
    #             os.rename(config_json_tmp,config_json)
    #             # 先完全清空原来的所有摄像头配置，等下会重新写入
    #             os.system("rm -f /etc/supervisord.d/box_*")
    #             os.system("rm -f /etc/nginx/conf.d/cam_*")
    #     else:
    #         # 如果 /home/md5_box.json 不存在，说明是盒子第一次拉取BI配置，将缓存的json直接更名为正式的json
    #         print('/home/md5_box.json does not exits , write to it now ~')
    #         os.rename(config_json_tmp,config_json)
    #
    #     for camera_config in data_json[key]:
    #         # cameras_config 是单个摄像头的配置信息，是一个字典或者json
    #         key_enable = 'enable'
    #         key_rtsp = 'rtsp'
    #         key_custom = 'custom'
    #         key_deviceid = 'deviceId'
    #         key_fps = 'fps'
    #         key_rtmp = 'rtmp'
    #         key_vpnPort = 'vpnPort'
    #         if camera_config[key_enable] :
    #             # "enable": true 开启推流
    #             if camera_config[key_custom] == "" :
    #                  # 生成转码命令
    #                  ffmpeg_command = ("ffmpeg -v verbose -rtsp_transport tcp -hwaccel vaapi -vaapi_device /dev/dri/renderD128"
    #                      " -i %s -vf format=nv12,hwupload -c:v h264_vaapi -an -g 50 -r %s -qp 25"
    #                      " -f flv -y %s") % (  camera_config[key_rtsp],camera_config[key_fps],camera_config[key_rtmp] )
    #                  #print ffmpeg_command
    #             elif camera_config[key_custom] == "-forward" :
    #                  # 生成转发命令
    #                  ffmpeg_command = ("ffmpeg -v verbose -rtsp_transport tcp -i %s -an -c:v copy -f flv"
    #                      " -y %s") % ( camera_config[key_rtsp],camera_config[key_rtmp] )
    #
    #             deviceid = camera_config[key_deviceid]
    #             vpnPort = camera_config[key_vpnPort]
    #             # 获得摄像头的IP地址
    #             rtsp = camera_config[key_rtsp]
    #             camera_ip = get_camip(rtsp)
    #             # 写入 supervisord 配置文件
    #             Write_conf(deviceid,ffmpeg_command)
    #             # 写入NGINX配置文件，启用摄像头反向代理
    #             Create_camera_proxy(deviceid,vpnPort,camera_ip)
    #         else :
    #             # "enable": false 关闭推流
    #             pass
    # else:
    #     pass
        #print "%s : %s" % ( key , data_json[key] )


# 写入supervisor的配置文件后，更新一下supervisor启动的相关守护进程
# 顺便重启一下NGINX
# os.system("/sbin/nginx -s reload  &>/dev/null")
# os.system("supervisorctl update &>/dev/null || systemctl restart supervisord &>/dev/null")
