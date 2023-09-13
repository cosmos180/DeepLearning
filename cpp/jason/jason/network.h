/*
 * @Author: your name
 * @Date: 2020-12-14 17:27:35
 * @LastEditTime: 2023-09-13 10:56:46
 * @LastEditors: bughero jinxinhou@tuputech.com
 * @Description: In User Settings Edit
 * @FilePath: /DeepLearning/cpp/jason/jason/network.h
 */

#include <cstdint>
#include <fstream>
#include <iostream>
#include <netdb.h>
#include <regex>
#include <stdio.h>
#include <streambuf>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/socket.h>

using namespace std;

class Network {
  private:
    /* data */
  public:
    uint64_t getIFMAC(const string &ifname) {
        ifstream iface("/sys/class/net/" + ifname + "/address");
        string str((istreambuf_iterator<char>(iface)), istreambuf_iterator<char>());
        if (str.length() > 0) {
            string hex = regex_replace(str, std::regex(":"), "");
            return stoull(hex, 0, 16);
        } else {
            return 0;
        }
    }

    void test() {
        string iface = "eth0";
        printf("%s: mac=%016lX\n", iface.c_str(), getIFMAC(iface));

        // FILE *pp = popen("ls -lh", "r"); // build pipe
        // if (!pp)
        //     return;

        // // collect cmd execute result
        // char tmp[1024];
        // while (fgets(tmp, sizeof(tmp), pp) != NULL) {
        //     std::cout << tmp << std::endl; // can join each line as string
        // }

        // pclose(pp);
    }
};
