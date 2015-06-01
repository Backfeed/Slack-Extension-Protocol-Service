Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = "bf-host"
  config.vm.provision 'shell', :privileged => false, :path => 'provision.sh'
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.synced_folder '.', '/home/vagrant'
end
