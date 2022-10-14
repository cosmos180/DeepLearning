/*
 * @Author: houjinxin
 * @Date: 2022-08-08 17:39:04
 * @Last Modified by: houjinxin
 * @Last Modified time: 2022-08-09 14:51:59
 */
#include <chrono>
#include <fcntl.h>
#include <fstream>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#include <nlohmann/json.hpp>

class IF_STREAM
{
public:
    static std::vector<std::string> split(std::string const &in, const std::string &regex)
    {
        std::string::size_type b = 0;
        std::vector<std::string> result;

        while ((b = in.find_first_not_of(regex.c_str(), b)) != std::string::npos)
        {
            auto e = in.find_first_of(regex.c_str(), b);
            result.emplace_back(in.substr(b, e - b));
            b = e;
        }
        return result;
    }

    void bufferToFile(const char *data, const uint32_t size, const char *path)
    {
        FILE *p_file = nullptr;

        p_file = fopen(path, "ab");

        fwrite(data, size, 1, p_file);
        fclose(p_file);
    }

    void test()
    {
        static const char kBoardConfigJsonPath[] = "/Users/cosmos/Desktop/local-bi-config/BoardConfig_huawei.json";
        static const char kThresholdJsonPath[] = "/Users/cosmos/Desktop/local-bi-config/ThresholdBag_huawei.json";

        // std::ifstream ifsBoardConfig(kBoardConfigJsonPath);
        // std::ifstream ifsThresholdBag(kThresholdJsonPath);

        // std::stringstream buffer;
        // buffer << ifsBoardConfig.rdbuf();
        // buffer << "*$$$$*";
        // buffer << ifsThresholdBag.rdbuf();

        // std::string m_strBoardConfig = buffer.str();
        // buffer.str(m_strBoardConfig);

        // printf("m_strBoardConfig: %d, %s\n", m_strBoardConfig.size(), m_strBoardConfig.c_str());

        // auto strArrayBizControll =
        //     split(m_strBoardConfig, "*$$$$*");
        // assert(strArrayBizControll.size() == 2);

        // printf("strArrayBizControll[0]: %d, %s\n", strArrayBizControll[0].size(), strArrayBizControll[0].c_str());
        // printf("strArrayBizControll[1]: %d, %s\n", strArrayBizControll[1].size(), strArrayBizControll[1].c_str());
        // printf("strArrayBizControll[1]: %s\n", (strArrayBizControll[0] + strArrayBizControll[1]).c_str());

        // bufferToFile(strArrayBizControll[0].c_str(), strArrayBizControll[0].size(), "/Users/cosmos/Desktop/debug.json");
        // bufferToFile(m_strBoardConfig.c_str(), m_strBoardConfig.size(), "/Users/cosmos/Desktop/debug.json");

        std::ifstream ifsBoard(kBoardConfigJsonPath);
        auto jBoard = nlohmann::json::parse(ifsBoard);
        // printf("jBoard: %s.\n", jBoard.dump().c_str());

        if (!jBoard.contains("data"))
        {
            return;
        }

        std::ifstream ifsThreshold(kThresholdJsonPath);
        auto jThresholdBag = nlohmann::json::parse(ifsThreshold);
        // printf("jThresholdBag: %s.\n", jThresholdBag.dump().c_str());

        int code = -1;
        if (!jThresholdBag.contains("code") || (code = jThresholdBag["code"].get<int>()) != 0)
        {
            return;
        }

        nlohmann::json jsonBag;
        jsonBag["board"] = jBoard;
        jsonBag["threshold"] = jThresholdBag;

        printf("jsonBag: size %d, %s.\n", jsonBag.dump().size(), jsonBag.dump().c_str());
    }
};