tar -zcvf - *.ini|openssl aes-256-cbc -salt  | dd of=inipak.enc
#~ cp *.ini configurations
