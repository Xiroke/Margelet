import { stringify } from "querystring"


export function GroupItem({title, subtitle, onClick}) {
    return (
        <div className='flex items-center gap-2 box-border max-h-[72px] hover:bg-[#353535]' onClick={onClick}>
            <div className="h-[72px] w-[72px] rounded-[12px] bg-[#E4E4E4]"></div>
            <div className='flex flex-col w-[236px]'>
                <div className="font-bold text-[#E4E4E4] leading-[20px] mt-1" >{title} <br></br>
                    <span className="font-normal text-[#939393] mb-1">{subtitle}</span>
                </div>
            </div>
        </div>
    )
}

export function ChatItem({children, onClick}) {
    return (
        <div className="p-0 text-[#E4E4E4] bg-[#353535] font-bold rounded-lg h-10 w-full flex items-center justify-center text-[18px]" onClick={onClick}>{children}</div>
    )
}

export function Participants({role, user_part}){
    // user_part: [{
    //     id: int,
    //     name: string,
    //}]
    return (
        <div className="">
            <div className="font-bold text-[18px] text-[#4D4D4D] mb-2">{role}</div>
            <div className="grid grid-cols-2 text-nowrap gap-2">
                {user_part.map(i => <ParticipantsItem key={i.id} name={i.name} />)}
            </div>
        </div>
    )
}

export function ParticipantsItem({name}){
    const avatar = (
        <div className="w-[32px] h-[32px] rounded-[4px] bg-[#E4E4E4] text-[#252525] flex items-center justify-center">{name[0]}</div>
    )
    
    if (name.length > 13) {
        name = name.slice(0, 10) + '...';
    }
    return (
        <div className="flex items-center gap-2">
            {avatar}
            <div className="text-[16px] text-[#E4E4E4]">{name}</div>
        </div>
    )
}