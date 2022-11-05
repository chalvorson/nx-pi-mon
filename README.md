# NetXMS Agent PI Monitor (nx-pi-mon.py)

## Purpose:
I built this to monitor the data quality of our FactoryTalk Historian servers.  Using a PLC tag as a heartbeat source for a PI Tag (ie. flip-flops between 0 and 1 every second), you can monitor the PI Interface Node for frozen tags or dropped connections between the PLC and FTLD Interface or FTLD Interface and Archive server.  The NetXMS server can then be configured to send a notification when the DCI value meets a threshold value.

>FYI: This program uses nxapush.exe to push the values to the NetXMS server.  The location is hardcoded to the default NetXMS install location.

## Example Usage:
Check if the data flow has stopped for more than 3 minutes and push the result to the NetXMS server under parameter "heartbeat".
        
    nx-pi-mon --tag PLC.Heartbeat -s -d 3 -p heartbeat

## Switches:
```
-t or --tag         Used to specify the PI Tag that you want to query.

-p or --param       The parameter name that you want to use in the 
                    NetXMS DCI. If not specified, it defaults to 
                    using the PI Tag name.

-s or --stale       When present, it checks the tag for staleness, 
                    otherwise it queries the PI tags current value.

-d or --duration    Duration, in minutes, to check for staleness.

-n or --nopush      Don't push the result to the NetXMS server.  
                    ie. Testing mode.
```

## NetXMS DCI Config
NetXMS pushed metrics are the easiest to setup.  Using the NetXMS Management Console, create a new DCI parameter with Origin: Push.  Choose an appropriate Display name and Data Type.  Then, for the Metric field, enter the parameter name that nx-pi-mon will push to the server.  
More precisely...
 - If you use the -p/--param switch and specify a parameter name, then set the Metric to the same parameter name.  
 - If you don't use the -p/--param switch, the default is to use the PI Tag name as the parameter name - so, enter the tag name in the Metric.

I haven't tested this out, but I believe that some PI Tag names won't be valid NetXMS DCI parameter names.  Which is why the -p/--param switch exists.

## Returns:
- Stale checking mode: *(-s is specified)*
  - Pushes True to the NetXMS server when the given PI tag has more than one unique data point in the given time span.  Otherwise, it returns false.
- Current value mode: *(-s is not specified)*
  - Pushes the current value of the PI Tag to the NetXMS server.

## Dependencies:
- [PIconnect](https://github.com/Hugovdberg/PIconnect): Tested with 0.9.1  *([pip install PIconnect](https://pypi.org/project/PIconnect/))*
- [PI AF SDK](https://osisoft.com): Tested with 2.10.9.253
- [NetXMS](https://netxms.org): Tested with 4.1.420+

## Known Issues:
*I have run into what seems like a .NET issue that I have yet to solve.  It could stem from the PIconnect library which uses a Python to .NET adapter.  Or, it may also be a PI AF SDK version issue.*
