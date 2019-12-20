echo y | bash install_factory_toolkit.run
test -e /usr/local/factory/enabled &&(
cp generic_rrt.test_list_cold_reboot_500.json /usr/local/factory/py/test/test_lists/generic_rrt.test_list.json
cp active_test_list.json /usr/local/factory/py/test/test_lists/active_test_list.json
reboot) || echo "[ERROR] CAN'T INSTALL SUCCESSFULLY...PLEASE CHECK OR CONTACT YOUR SW!!!!"
