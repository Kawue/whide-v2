struct Record{
int key;
double value;
};

struct ring{
	int start;
	int stop;
};

//structure used for the storage of the distance and the coresponding idx during bmu search
struct dist2Idx{
	double dist;
	int idx;
};

struct SOMnode{
    double x;
    double y;
};

struct node{
    long left;
    double leftWeight;
    long right;
    double rightWeight;
};