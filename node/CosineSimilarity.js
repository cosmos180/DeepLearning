const fs = require('fs');
const math = require('mathjs');

// 从JSON文件中读取向量数据
function readVectorFromFile(filePath) {
  const fileContent = fs.readFileSync(filePath, 'utf8');
  const vectorData = JSON.parse(fileContent);

  console.log('trackID: ', vectorData.strTrackId)
  return vectorData.faceFeature;
}

// 计算两个向量之间的余弦相似度
function calculateCosineSimilarity(vector1, vector2) {
  console.info(`vector1 length: ${vector1.length}`)
  console.info(`vector2 length: ${vector2.length}`)

  if (vector1.length < 512) {
    while (vector1.length < 512) {
      vector1.push(0);
    }
  }

  if (vector2.length < 512) {
    while (vector2.length < 512) {
      vector2.push(0);
    }
  }

  const dotProduct = math.dot(vector1, vector2);
  const magnitude1 = math.norm(vector1);
  const magnitude2 = math.norm(vector2);
  const similarity = dotProduct / (magnitude1 * magnitude2);
  return similarity;
}

// 读取向量文件

const kPath = "/home/bughero/Desktop"
const vectorFile_A = "BaseHelper_ReID/1690269711320_176.json";
const vectorFile_B = "BaseHelper_ReID/1690270175380_184.json";
// const vectorFile_B = "handle_34/1689840949069_116.json";

const vector1 = readVectorFromFile(`${kPath}/${vectorFile_A}`);
const vector2 = readVectorFromFile(`${kPath}/${vectorFile_B}`);

// 计算余弦相似度
const similarity = calculateCosineSimilarity(vector1, vector2);
console.log('Cosine Similarity:', similarity);