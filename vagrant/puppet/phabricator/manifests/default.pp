# Basic Puppet Apache manifest

$apache2_sites = "/etc/apache2/sites"
$dev_dir       = "${phab_dir}/instances/dev"
$document_root = "${dev_dir}/phabricator/webroot"
$std_path      = "/usr/bin:/usr/sbin:/bin"
$http_proxy    = ""

file { 'apt-proxyconfig' :
  path    => '/etc/apt/apt.conf.d/95proxies',
  ensure  => present,
  content => "Acquire::http::proxy \"${http_proxy}\";",
  notify  => Exec['apt-update'],
}

exec { 'apt-update':
    command     => 'apt-get update',
    refreshonly => true,
    path        => $std_path,
}

class { 'apache':
	default_vhost => false,
}


#RewriteRule ^/rsrc/(.*)     -                       [L,QSA]
#RewriteRule ^/favicon.ico   -                       [L,QSA]
apache::vhost { 'local-phabricator':
	servername => "localhost",
	docroot => "${document_root}",
	rewrite_rule => '^(.*)$          /index.php?__path__=$1  [B,L,QSA]',
	setenv => 'PHABRICATOR_ENV production',
}

class otherpackages {
    $packages = ["git-core", "mysql-server", "php5", "dpkg-dev"]
    $php_packages = ["php5-mysql", "php5-gd", "php5-dev", "php5-curl", "php-apc", "php5-cli"]

    package { $packages: ensure     => installed, }
    package { $php_packages: ensure => installed, }
}

class phabricator {

    # puppet won't create parent directories and will fail if we don't
    # manually specify each of them as separate dependencies
    # it does automatically create them in the correct order though
    file { "/phabricator/instances/dev":
        ensure => directory,
    }
    file { "/phabricator/instances":
        ensure => directory,
    }
    file { "/phabricator":
        ensure => directory,
    }

    define phabgitclone ($repo = $title) {
        $proxy_string = "http_proxy=${http_proxy}"
        $github_string = "http://github.com/facebook"
        exec { "git clone ${github_string}/${repo} ${dev_dir}/${repo}":
            path        => $std_path,
            creates     => "${dev_dir}/${repo}",
            environment => $proxy_string,
        }
    }

    phabgitclone {'phabricator':}
    phabgitclone {'libphutil':}
    phabgitclone {'arcanist':}
}

class phabricatordb {
    file { "initial.db":
	path   => "${phab_dir}/initial.db",
	source => "puppet:///modules/phabricator/initial.db",
	ensure => present,
    }

    exec { "mysql < ${phab_dir}/initial.db && ${dev_dir}/phabricator/bin/storage upgrade --force":
        path    => $std_path,
        unless  => "${dev_dir}/phabricator/bin/storage status",
	require => File["initial.db"],
    }
}

# declare our entities
apache::mod { "rewrite": }
class {'otherpackages':}
class {'phabricator':}
class {'phabricatordb':}

# declare our dependencies
#Class['apache']        <- File['apt-proxyconfig']
#Class['otherpackages'] <- File['apt-proxyconfig']
#Class['phabricator']   <- Class['apache']
#Class['phabricator']   <- Class['otherpackages']
#Class['phabricatordb'] <- Class['phabricator']
