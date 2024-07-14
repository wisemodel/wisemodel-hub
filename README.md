# wisemodel-hub
wisemodel-hub


## 常见问题
1.上传文件时报错：NotOpenSSLWarning: urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020

解决办法：将 urllib3 降低到 2.0.0 以下：
```shell
pip uninstall urllib3  
pip install 'urllib3<2.0'

```
