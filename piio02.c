//this code is based on the char driver lkmdata
//it was modified to turn on the LED when someting is written to it
//and to turn the LED off when sometinh is read from here
//honestly reconsider using this code, the previous code was way more efficient.....

#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/uaccess.h>
#include <linux/gpio.h>

static int Major = 400;
#define  DEVICE_NAME "piiodev"

static struct class*  chardevClass  = NULL;
static struct device* chardevDevice = NULL;
#define  CLASS_NAME  "piiodata"

typedef struct lkm_data {
	unsigned char data[256];
	unsigned long len;
	char type;
} LKM_DATA;
LKM_DATA lkm_data;

MODULE_LICENSE("GPL");
MODULE_AUTHOR("slepy");
MODULE_DESCRIPTION("used to pass the GPIO to trun it on or off");
MODULE_VERSION("0.3");


static ssize_t lkmdata_read(struct file *file, char *buffer, size_t length, loff_t * offset){
    pr_info("%s %u\n", __func__, length);
    strcpy(lkm_data.data, "This is from LKM");
    	lkm_data.len = 32;
    	lkm_data.type = 'w';
    	copy_to_user(buffer, &lkm_data, sizeof(lkm_data));

	gpio_set_value(23, 0);
   	gpio_unexport(23);
   	gpio_free(23);
    return 0;
}


static ssize_t lkmdata_write(struct file *file, const char *buffer, size_t length, loff_t * offset){
    pr_info("%s %u\n", __func__, length);
    copy_from_user(&lkm_data, buffer, length);

    gpio_request(23, "Led"); //if have time modify this so that the data taken from userspace
    gpio_direction_output(23, 1);// will be used as a GPIO
    gpio_export(23, false);
    gpio_set_value(23, 1);
    return length;
}

struct file_operations lkmdata_fops = {
    .owner = THIS_MODULE,
    .read = lkmdata_read,
    .write = lkmdata_write,
};

static int __init piio_init(void){
	 printk(KERN_INFO "chardev: Initializing the chardev LKM\n");
		   Major = register_chrdev(0, DEVICE_NAME, &lkmdata_fops);
		      if (Major<0){
		         printk(KERN_ALERT "chardev failed to register a major number\n");
		         return Major;
		      }

		   // Register the device class
		   chardevClass = class_create(THIS_MODULE, CLASS_NAME);
		   if (IS_ERR(chardevClass)){
		      unregister_chrdev(Major, DEVICE_NAME);
		      printk(KERN_ALERT "Failed to register device class\n");
		      return PTR_ERR(chardevClass);
		   }

		   // Register the device driver
		   chardevDevice = device_create(chardevClass, NULL, MKDEV(Major, 0), NULL, DEVICE_NAME);
		   if (IS_ERR(chardevDevice)){
		      class_destroy(chardevClass);
		      unregister_chrdev(Major, DEVICE_NAME);
		      printk(KERN_ALERT "Failed to create the device\n");
		      return PTR_ERR(chardevDevice);
		   }
   return 0;
}

static void __exit piio_exit(void){
	   gpio_set_value(23, 0);
   	   gpio_unexport(23);
   	   gpio_free(23);
	   device_destroy(chardevClass, MKDEV(Major, 0));
	   class_unregister(chardevClass);
	   class_destroy(chardevClass);
	   unregister_chrdev(Major, DEVICE_NAME);
}

module_init(piio_init);
module_exit(piio_exit);
