#include <iostream>
#include "opencv2/opencv.hpp"
using namespace std;
using namespace cv;
int main(int argc, char* argv[])
{
         //读入图像，并将之转为单通道图像
         Mat im = imread("test.jpg", 0);
         //  //请一定检查是否成功读图
         if( im.empty() )
         {
              cout << "Can not load image." << endl;
              return -1;
         }
                 //进行 Canny 操作，并将结果存于 result
         Mat result;
         Canny(im, result, 50, 150);
         //           //保存结果
         imwrite("test2.jpg", result);
         return 0;
}
