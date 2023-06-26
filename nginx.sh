if [ ! -d "/tmp/nginx" ]; then
    mkdir /tmp/nginx
fi

nginx -c ~/$REPL_SLUG/nginx.conf -e ~/$REPL_SLUG/debug/error.log -g 'daemon off; pid /tmp/nginx/nginx.pid;' -p ~/$REPL_SLUG/debug;