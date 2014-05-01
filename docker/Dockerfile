FROM ubuntu:raring
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y apache2 libapache2-mod-auth-mysql libapache2-mod-php5
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y git
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y php5 php5-mysql php5-mcrypt php5-cli php5-gd php5-dev php5-curl php-apc php5-cli
RUN mysql_install_db
RUN a2enmod rewrite
RUN mkdir -p /var/www/phabricator
RUN cd /var/www/phabricator; git clone https://github.com/facebook/phabricator; cd phabricator; git checkout df8474d778048a7364b2e332a1e4cae55d93291e
RUN cd /var/www/phabricator; git clone https://github.com/facebook/libphutil; cd libphutil; git checkout 0b9f193303dfae4f9204d8f577e2bd45acd4963f
RUN cd /var/www/phabricator; git clone https://github.com/facebook/arcanist; cd arcanist; git checkout 42ae7cd92f92e026bdd604e659d2bc23e9352baa
ADD apache-phabricator.conf /etc/apache2/sites-available/phabricator.conf
RUN a2ensite phabricator.conf
ADD start-in-vm.sh /start-in-vm.sh
ADD initial.db /intial.db
RUN chmod +x /start-in-vm.sh
CMD ["/start-in-vm.sh"]
EXPOSE 80
