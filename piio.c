#include <linux/module.h>
#include <linux/gpio.h>

static unsigned int Led = 23;

int __init piio_init(void){
    if (!gpio_is_valid(Led)){
    	printk(KERN_INFO "piio: invalid GPIO\n");
    return -ENODEV;
   }
	   gpio_request(Led, "Led");
	   gpio_direction_output(Led, 1);
	   gpio_export(Led, false);
       gpio_set_value(Led, 1);
    return 0;
}

void __exit piio_exit(void){
   gpio_set_value(Led, 0);
   gpio_unexport(Led);
   gpio_free(Led);
   printk("piio unloaded\n");
}

module_init(piio_init);
module_exit(piio_exit);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("Slepy");
MODULE_DESCRIPTION("Controll LED");
MODULE_VERSION("0.1");