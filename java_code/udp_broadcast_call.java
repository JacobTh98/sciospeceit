String host = "255.255.255.255"; int port = 8888;
char data[] = {0xD1, 0, 0xD1}; String message = new String(data);
//Broadcast address
//the destination port of the broadcast
//bc char is unsigned
try{
    InetAddress adds = InetAddress.getByName(host);
    DatagramSocket ds = new DatagramSocket();
    DatagramPacket dp = new DatagramPacket(message.getBytes(), message.length(),
    adds, port);
        ds.send(dp);
        ds.close();
}
catch (UnknownHostException e){ e.printStackTrace();
} catch (SocketException e) { e.printStackTrace();
} catch (IOException e){ e.printStackTrace();
}
byte[] buf = new byte[1024];
try {
    //Bind port
    //store the message sent
    DatagramSocket ds = null;
    DatagramPacket dp = null;
    ds = new DatagramSocket(port);
    dp = new DatagramPacket(buf, buf.length);
    System.out.println("The listening broadcast port is open:"+port);
    ds.receive(dp);
    ds.close();
    System.out.print("Recieved Msg:");
    for(int j=0;j<dp.getLength();j++) {
    System.out.print(" "+String.format("%02X", buf[j]));
    }
        System.out.println("");
        System.out.print("Received from:"+dp.getAddress());
}
catch (SocketException e) { e.printStackTrace();
} catch (IOException e){ e.printStackTrace();
}