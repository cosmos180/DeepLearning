#! /usr/bin/bash
###
 # @Author: bughero jinxinhou@tuputech.com
 # @Date: 2023-10-18 15:03:22
 # @LastEditors: bughero jinxinhou@tuputech.com
 # @LastEditTime: 2023-10-24 19:27:50
 # @FilePath: /DeepLearning/shell/ffmpeg_mulprocess.sh
 # @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
### 

# 本地计算机上运行
export XAUTHORITY=$HOME/.Xauthority
export DISPLAY=:0

max_process_count=$1
i=1

start=`date +"%s"`
for (( i=0; i<${max_process_count}; i++ ))
do
    {
        echo "multiprocess-${i}"
        # ffmpeg -c:v h264 -i 20230911-162554.mp4 -c:v libx264 -f mp4 output_test_${i}.mp4 -benchmark
        obs -m &
        sleep 3
    }  #将上述程序块放到后台执行
done
wait    #等待上述程序结束
end=`date +"%s"`
echo "time: " `expr $end - $start`

rm output_test_*.mp4
