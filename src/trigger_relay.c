#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

int main()
{
    setuid( 0 );
    system( "DASHVEND_DIRECTORY/bin/trigger_relay.sh" );
    return 0;
}
