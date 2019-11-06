function addRow(host_name, host_address, host_status, link){
        var tbody = document.getElementById('hl').getElementsByTagName("TBODY")[0];
        var row = document.createElement("TR")
        var hostname = document.createElement("TD")
        hostname.innerHTML = "<a href='" + link + "'>" + host_name + "</a>"
        var hostaddress = document.createElement("TD")
        hostaddress.appendChild (document.createTextNode(host_address))
        
        var hoststatus = document.createElement("TD")
        
        if (host_status){
            hoststatus.innerHTML = "<b style='color:green'>Connected</b>"
        }else{
            hoststatus.innerHTML = "<b style='color:red'>Disconnected</b>"
        }
        
        row.appendChild(hostname);
        row.appendChild(hostaddress);
        row.appendChild(hoststatus);
        
        tbody.appendChild(row);
    }

