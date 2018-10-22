#!/bin/bash
list_of_users_in_wheel=$(getent group mcs-wheel | cut -d':' -f4 | awk -F "," '{
   for (i=1;i<=NF;i++)
      print $i}' | sort )
list_of_users_in_cci=$(getent group cci-techstaff | cut -d':' -f4 | awk -F "," '{
   for (i=1;i<=NF;i++)
      print $i}' | sort )

list_of_users_in_wheel="$list_of_users_in_wheel jws337 mjr426"
temp="$list_of_users_in_wheel"
temp="$temp $list_of_users_in_cci"
list_of_root_users=$(echo $temp | xargs -n1 | sort -u)

passphrased_keys()
{
   rm ../roles/ssh/files/keys_passphrased/*
	echo "wheel_pass:" > ../roles/ssh/defaults/main.yml

	for user in $list_of_users_in_wheel
	do
		grep -q "Proc-Type: 4,ENCRYPTED" /home/$user/.ssh/id_rsa &> /dev/null# Check for passphrase
		if ! [ $? -ne 0 ] # Only do something if it was found
		then
			echo "  - $user" >> ../roles/ssh/defaults/main.yml
         cp /home/$user/.ssh/id_rsa ../roles/ssh/files/keys_passphrased/"$user".key
			chown $SUDO_USER.$SUDO_USER ../roles/ssh/files/keys_passphrased/"$user".key
		fi
	done

	chown $SUDO_USER.$SUDO_USER ../roles/ssh/defaults/main.yml
}

make_auth_keys()
{
	rm ../roles/ssh/files/authorized_keys_ws
	for user in $list_of_root_users
	do
		if [ -f /home/$user/.ssh/authorized_keys ]
		then
			echo $user has access to workstations
			cat /home/$user/.ssh/authorized_keys >> ../roles/ssh/files/authorized_keys_ws
		fi
	done
   rm ../roles/ssh/files/authorized_keys_all
   for user in $list_of_users_in_wheel
	do
		if [ -f /home/$user/.ssh/authorized_keys ]
		then
			echo $user has access to all servers
         cat /home/$user/.ssh/authorized_keys >> ../roles/ssh/files/authorized_keys_all
		fi
	done

	chown $SUDO_USER.$SUDO_USER ../roles/ssh/files/authorized_keys*
}

make_known_hosts()
{
echo -n "" > ../roles/ssh/files/known_hosts/known_hosts.pub
echo -n "" > ../roles/ssh/files/known_hosts/known_hosts.pri
echo -n "" > ../roles/ssh/files/known_hosts/precise_known_hosts.pub
echo -n "" > ../roles/ssh/files/known_hosts/precise_known_hosts.pri

for host in ../roles/ssh/files/host_keys/*
do
	hostname=$(echo $host | cut -d'/' -f6)
	public_host_string=$(host $hostname.blah.com 8.8.8.8 || host $hostname.blah.com 8.8.8.8 || host $hostname.blah.com 8.8.8.8)
	private_host_string=$(host $hostname.blah.com 8.8.8.8 || host $hostname.blah.com 8.8.8.8 || host $hostname.blah.com 8.8.8.8)
    found_public=$?
    found_private=$?
	pri_full_name=$(echo "$private_host_string" | grep ^$hostname | head -1 | awk '{print $1}')
	pub_full_name=$(echo "$public_host_string" | grep ^$hostname | head -1 | awk '{print $1}')
	public_host_string=$(echo "$public_host_string" | grep ^$hostname| awk '{print $NF}')
	private_host_string=$(echo "$private_host_string" | grep ^$hostname | awk '{print $NF}')
	for key in $host/*_*_*_*.pub
	do
		if [[ $key == *"ed25519"* ]] # Skip ed255519 for precise machines
		then
			echo $hostname $(cat $key | awk '{print $1,$2}') | tee -a  ../roles/ssh/files/known_hosts/known_hosts.pri ../roles/ssh/files/known_hosts/known_hosts.pub > /dev/null

            if [ $found_private -eq 0 ]
            then
			    echo $pri_full_name $(cat $key | awk '{print $1,$2}') >> ../roles/ssh/files/known_hosts/known_hosts.pri
			    for address in $(echo $private_host_string)
			    do
				    echo $address $(cat $key | awk '{print $1,$2}') >> ../roles/ssh/files/known_hosts/known_hosts.pri
			    done
            fi
		
            if [ $found_public -eq 0 ]
            then
			    echo $pub_full_name $(cat $key | awk '{print $1,$2}') >> ../roles/ssh/files/known_hosts/known_hosts.pub
			    for address in $(echo $public_host_string)
			    do
				    echo $address $(cat $key | awk '{print $1,$2}') >> ../roles/ssh/files/known_hosts/known_hosts.pub
			    done
            fi
		else
			echo $hostname $(cat $key | awk '{print $1,$2}') | tee -a  ../roles/ssh/files/known_hosts/known_hosts.pri ../roles/ssh/files/known_hosts/known_hosts.pub ../roles/ssh/files/known_hosts/precise_known_hosts.pri ../roles/ssh/files/known_hosts/precise_known_hosts.pub > /dev/null

            if [ $found_private -eq 0 ]
            then
			    echo $pri_full_name $(cat $key | awk '{print $1,$2}') | tee -a ../roles/ssh/files/known_hosts/known_hosts.pri ../roles/ssh/files/known_hosts/precise_known_hosts.pri > /dev/null
			    for address in $(echo $private_host_string)
			    do
				    echo $address $(cat $key | awk '{print $1,$2}') | tee -a ../roles/ssh/files/known_hosts/known_hosts.pri ../roles/ssh/files/known_hosts/precise_known_hosts.pri > /dev/null
			    done
            fi
		
            if [ $found_public -eq 0 ]
            then
			    echo $pub_full_name $(cat $key | awk '{print $1,$2}') | tee -a ../roles/ssh/files/known_hosts/known_hosts.pub ../roles/ssh/files/known_hosts/precise_known_hosts.pub > /dev/null
			    for address in $(echo $public_host_string)
			    do
				    echo $address $(cat $key | awk '{print $1,$2}') | tee -a ../roles/ssh/files/known_hosts/known_hosts.pub ../roles/ssh/files/known_hosts/precise_known_hosts.pub > /dev/null
			    done
            fi
		fi
	done
done

}


passphrased_keys
make_auth_keys
make_known_hosts
chmod 600 ../roles/ssh/files/host_keys/*/*key
