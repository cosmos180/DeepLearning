/*
 * @Author: your name
 * @Date: 2020-12-14 17:27:35
 * @LastEditTime: 2020-12-14 18:25:18
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /conan/test_package/target/network.h
 */

#include <cstdint>
#include <fstream>
#include <streambuf>
#include <regex>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netdb.h>
#include <stdio.h>
#include <string.h>
#include <iostream>

using namespace std;

class Network
{
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
        printf("%s: mac=%016llX\n", iface.c_str(), getIFMAC(iface));

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
